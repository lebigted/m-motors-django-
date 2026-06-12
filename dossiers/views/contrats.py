from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Contrat
from ..serializers import (
    ContratSerializer, ContratCreateSerializer, ContratKmSerializer,
    ContratSignerSerializer, ContratValiderSignatureSerializer,
    ContratValiderPaiementSerializer, ContratRDVProposerSerializer,
    ContratRDVConfirmerSerializer, ContratReceptionSerializer, ContratLivrerSerializer,
)


class ContratViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ContratCreateSerializer
        if self.action == 'update_km':
            return ContratKmSerializer
        return ContratSerializer

    def get_queryset(self):
        user   = self.request.user
        params = self.request.query_params
        if user.is_admin and params.get('mine') != 'true':
            qs = Contrat.objects.select_related('client', 'vehicle', 'dossier').all()
            if cl := params.get('client_id'):
                qs = qs.filter(client_id=cl)
            if s := params.get('statut'):
                qs = qs.filter(statut=s)
            return qs
        return Contrat.objects.filter(client=user).select_related('vehicle', 'dossier')

    def _check_statut(self, contrat, attendu):
        if contrat.statut != attendu:
            return Response(
                {'detail': f"Action impossible : statut actuel « {contrat.get_statut_display()} »."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    @action(detail=True, methods=['patch'], url_path='signer')
    def signer(self, request, pk=None):
        contrat = self.get_object()
        if contrat.client != request.user:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        err = self._check_statut(contrat, 'a_signer')
        if err:
            return err
        s = ContratSignerSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        contrat.signature_nom  = s.validated_data['signature_nom']
        contrat.signature_date = timezone.now()
        contrat.statut         = 'signe'
        contrat.save()
        return Response(ContratSerializer(contrat, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='valider_signature')
    def valider_signature(self, request, pk=None):
        if not request.user.is_admin:
            return Response({'detail': 'Réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)
        contrat = self.get_object()
        err = self._check_statut(contrat, 'signe')
        if err:
            return err
        s = ContratValiderSignatureSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        contrat.signature_validee_at = timezone.now()
        contrat.statut               = 'a_payer'
        if s.validated_data.get('notes_admin'):
            contrat.notes_admin = s.validated_data['notes_admin']
        if s.validated_data.get('commentaire'):
            contrat.commentaire = s.validated_data['commentaire']
        contrat.save()
        return Response(ContratSerializer(contrat, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='valider_paiement')
    def valider_paiement(self, request, pk=None):
        if not request.user.is_admin:
            return Response({'detail': 'Réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)
        contrat = self.get_object()
        err = self._check_statut(contrat, 'a_payer')
        if err:
            return err
        s = ContratValiderPaiementSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        contrat.paiement_mode       = s.validated_data['paiement_mode']
        contrat.paiement_date       = s.validated_data['paiement_date']
        contrat.paiement_reference  = s.validated_data.get('paiement_reference', '')
        contrat.paiement_verifie_at = timezone.now()
        contrat.statut              = 'paye'
        if s.validated_data.get('notes_admin'):
            contrat.notes_admin = s.validated_data['notes_admin']
        if s.validated_data.get('commentaire'):
            contrat.commentaire = s.validated_data['commentaire']
        if contrat.vehicle.status != 'vendu':
            contrat.vehicle.status = 'vendu'
            contrat.vehicle.save()
        contrat.save()
        return Response(ContratSerializer(contrat, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='proposer_rdv')
    def proposer_rdv(self, request, pk=None):
        if not request.user.is_admin:
            return Response({'detail': 'Réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)
        contrat = self.get_object()
        err = self._check_statut(contrat, 'paye')
        if err:
            return err
        s = ContratRDVProposerSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        contrat.rdv_dates_proposees = [str(d) for d in s.validated_data['rdv_dates_proposees']]
        contrat.rdv_lieu            = s.validated_data.get('rdv_lieu', '')
        contrat.statut              = 'rdv_propose'
        if s.validated_data.get('notes_admin'):
            contrat.notes_admin = s.validated_data['notes_admin']
        if s.validated_data.get('commentaire'):
            contrat.commentaire = s.validated_data['commentaire']
        contrat.save()
        return Response(ContratSerializer(contrat, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='confirmer_rdv')
    def confirmer_rdv(self, request, pk=None):
        contrat = self.get_object()
        if contrat.client != request.user:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        err = self._check_statut(contrat, 'rdv_propose')
        if err:
            return err
        s = ContratRDVConfirmerSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        date_choisie = str(s.validated_data['rdv_date_confirmee'])
        if date_choisie not in contrat.rdv_dates_proposees:
            return Response({'detail': 'Date non proposée. Choisissez parmi les dates disponibles.'},
                            status=status.HTTP_400_BAD_REQUEST)
        contrat.rdv_date_confirmee = s.validated_data['rdv_date_confirmee']
        contrat.statut             = 'rdv_confirme'
        contrat.save()
        return Response(ContratSerializer(contrat, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='confirmer_reception')
    def confirmer_reception(self, request, pk=None):
        contrat = self.get_object()
        if contrat.client != request.user:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        err = self._check_statut(contrat, 'rdv_confirme')
        if err:
            return err
        s = ContratReceptionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        contrat.client_reception_nom  = s.validated_data['client_reception_nom']
        contrat.client_reception_date = timezone.now()
        contrat.statut                = 'reception_signee'
        contrat.save()
        return Response(ContratSerializer(contrat, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='livrer')
    def livrer(self, request, pk=None):
        if not request.user.is_admin:
            return Response({'detail': 'Réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)
        contrat = self.get_object()
        err = self._check_statut(contrat, 'reception_signee')
        if err:
            return err
        s = ContratLivrerSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        contrat.livraison_date    = s.validated_data['livraison_date']
        contrat.admin_remise_nom  = s.validated_data['admin_remise_nom']
        contrat.admin_remise_date = timezone.now()
        contrat.statut            = 'actif'
        if s.validated_data.get('notes_admin'):
            contrat.notes_admin = s.validated_data['notes_admin']
        if s.validated_data.get('commentaire'):
            contrat.commentaire = s.validated_data['commentaire']
        contrat.save()
        return Response(ContratSerializer(contrat, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='km')
    def update_km(self, request, pk=None):
        contrat = self.get_object()
        if contrat.client != request.user and not request.user.is_admin:
            return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        s = ContratKmSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        km = s.validated_data['km_actuel']
        if km < contrat.km_initial:
            return Response(
                {'detail': 'Le kilométrage ne peut pas être inférieur au kilométrage initial.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        contrat.km_actuel = km
        contrat.save()
        return Response(ContratSerializer(contrat).data)
