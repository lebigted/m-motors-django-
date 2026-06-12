from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import SAVTicket, SAVMessage
from ..serializers import (
    SAVTicketSerializer, SAVTicketCreateSerializer,
    SAVTicketTraiterSerializer, SAVMessageSerializer,
)


class SAVTicketViewSet(viewsets.GenericViewSet,
                       viewsets.mixins.ListModelMixin,
                       viewsets.mixins.RetrieveModelMixin,
                       viewsets.mixins.CreateModelMixin):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = SAVTicketSerializer

    def get_queryset(self):
        if self.request.user.is_admin:
            return SAVTicket.objects.select_related('client').all()
        return SAVTicket.objects.filter(client=self.request.user)

    def create(self, request, *args, **kwargs):
        if request.user.is_admin:
            return Response({'detail': 'Réservé aux clients.'}, status=status.HTTP_400_BAD_REQUEST)
        s = SAVTicketCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        ticket = SAVTicket.objects.create(
            client=request.user,
            sujet=s.validated_data['sujet'],
            description=s.validated_data['description'],
        )
        return Response(SAVTicketSerializer(ticket, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='traiter')
    def traiter(self, request, pk=None):
        if not request.user.is_admin:
            return Response({'detail': 'Réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)
        ticket = self.get_object()
        if ticket.statut != 'en_attente':
            return Response({'detail': 'Ce ticket a déjà été traité.'}, status=status.HTTP_400_BAD_REQUEST)
        s = SAVTicketTraiterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        ticket.statut  = s.validated_data['statut']
        ticket.reponse = s.validated_data.get('reponse', '')
        ticket.save()
        if ticket.statut == 'accepte' and ticket.reponse:
            SAVMessage.objects.create(ticket=ticket, auteur=request.user, contenu=ticket.reponse)
        return Response(SAVTicketSerializer(ticket, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='cloturer')
    def cloturer(self, request, pk=None):
        if not request.user.is_admin:
            return Response({'detail': 'Réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)
        ticket = self.get_object()
        if ticket.statut != 'accepte':
            return Response({'detail': 'Seul un suivi ouvert peut être clôturé.'},
                            status=status.HTTP_400_BAD_REQUEST)
        ticket.statut = 'cloture'
        ticket.save()
        return Response(SAVTicketSerializer(ticket, context={'request': request}).data)

    @action(detail=True, methods=['get', 'post'], url_path='messages')
    def messages(self, request, pk=None):
        ticket = self.get_object()
        if ticket.statut not in ('accepte', 'cloture'):
            return Response(
                {'detail': "La messagerie n'est disponible que pour les tickets acceptés."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.is_admin and ticket.client != request.user:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'GET':
            msgs = ticket.sav_messages.select_related('auteur').all()
            return Response(SAVMessageSerializer(msgs, many=True).data)

        if ticket.statut == 'cloture':
            return Response({'detail': 'Ce suivi SAV est clôturé.'}, status=status.HTTP_400_BAD_REQUEST)
        contenu = request.data.get('contenu', '').strip()
        if not contenu:
            return Response({'detail': 'Le message ne peut pas être vide.'},
                            status=status.HTTP_400_BAD_REQUEST)
        msg = SAVMessage.objects.create(ticket=ticket, auteur=request.user, contenu=contenu)
        return Response(SAVMessageSerializer(msg).data, status=status.HTTP_201_CREATED)
