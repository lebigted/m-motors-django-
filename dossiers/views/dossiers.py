from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from ..models import Dossier, Message
from ..serializers import (
    DossierSerializer, DossierCreateSerializer,
    DossierDecisionSerializer, DocumentSerializer, MessageSerializer,
)


class DossierViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return DossierCreateSerializer
        return DossierSerializer

    def get_queryset(self):
        user   = self.request.user
        params = self.request.query_params
        force_mine = params.get('mine') == 'true'

        if user.is_admin and not force_mine:
            qs = Dossier.objects.select_related('client', 'vehicle').prefetch_related(
                'documents', 'messages', 'messages__auteur'
            )
            if self.action == 'list':
                if s := params.get('status'):
                    qs = qs.filter(status=s)
                if t := params.get('type'):
                    qs = qs.filter(type=t)
                if cl := params.get('client_id'):
                    qs = qs.filter(client_id=cl)
                if params.get('archived') == 'true':
                    qs = qs.filter(archived=True)
                elif params.get('archived') != 'all':
                    qs = qs.filter(archived=False)
            return qs
        return Dossier.objects.filter(client=user).select_related('vehicle').prefetch_related(
            'documents', 'messages', 'messages__auteur'
        )

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        dossier = self.get_object()
        if hasattr(dossier, 'contrat'):
            dossier.contrat.delete()
        dossier.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='archive')
    def archive(self, request, pk=None):
        if not request.user.is_admin:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        dossier = self.get_object()
        dossier.archived = not dossier.archived
        dossier.save()
        return Response({'archived': dossier.archived,
                         'detail': 'Archivé.' if dossier.archived else 'Désarchivé.'})

    @action(detail=True, methods=['patch'], url_path='decision')
    def decision(self, request, pk=None):
        if not request.user.is_admin:
            return Response({'detail': 'Action réservée aux administrateurs.'},
                            status=status.HTTP_403_FORBIDDEN)
        dossier = self.get_object()
        serializer = DossierDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dossier.status = serializer.validated_data['status']
        dossier.motif  = serializer.validated_data.get('motif', '')
        dossier.save()
        return Response(DossierSerializer(dossier, context={'request': request}).data)

    @action(detail=True, methods=['get', 'post'], url_path='messages')
    def messages(self, request, pk=None):
        dossier = self.get_object()

        if request.method == 'GET':
            msgs = dossier.messages.all()
            if request.user.is_admin:
                msgs.filter(lu_admin=False).exclude(auteur=request.user).update(lu_admin=True)
            else:
                msgs.filter(lu_client=False).exclude(auteur=request.user).update(lu_client=True)
            return Response(MessageSerializer(msgs, many=True).data)

        contenu = request.data.get('contenu', '').strip()
        if not contenu:
            return Response({'detail': 'Le contenu est obligatoire.'},
                            status=status.HTTP_400_BAD_REQUEST)
        msg = Message.objects.create(dossier=dossier, auteur=request.user, contenu=contenu)
        return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], url_path='documents',
            parser_classes=[MultiPartParser, FormParser])
    def documents(self, request, pk=None):
        dossier = self.get_object()

        if request.method == 'GET':
            return Response(DocumentSerializer(
                dossier.documents.all(), many=True, context={'request': request}
            ).data)

        if dossier.client != request.user and not request.user.is_admin:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        fichier  = request.FILES.get('fichier')
        type_doc = request.data.get('type_doc')
        if not fichier:
            return Response({'detail': 'Aucun fichier reçu.'}, status=status.HTTP_400_BAD_REQUEST)
        if not type_doc:
            return Response({'detail': 'type_doc manquant.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DocumentSerializer(
            data={'dossier': dossier.pk, 'type_doc': type_doc, 'fichier': fichier},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
