from rest_framework import serializers
from ..models import Contrat
from accounts.serializers import UserSerializer
from vehicles.serializers import VehicleSerializer


class ContratSerializer(serializers.ModelSerializer):
    client_info           = UserSerializer(source='client',  read_only=True)
    vehicle_info          = VehicleSerializer(source='vehicle', read_only=True)
    type_display          = serializers.CharField(source='get_type_display',          read_only=True)
    statut_display        = serializers.CharField(source='get_statut_display',        read_only=True)
    paiement_mode_display = serializers.CharField(source='get_paiement_mode_display', read_only=True)
    dossier_ref           = serializers.SerializerMethodField()
    etape_courante        = serializers.SerializerMethodField()

    class Meta:
        model  = Contrat
        fields = [
            'id', 'dossier', 'dossier_ref',
            'client', 'client_info',
            'vehicle', 'vehicle_info',
            'type', 'type_display',
            'montant', 'date_debut', 'date_fin',
            'km_initial', 'km_actuel',
            'statut', 'statut_display', 'etape_courante',
            'notes_admin', 'commentaire',
            'signature_nom', 'signature_date', 'signature_validee_at',
            'paiement_mode', 'paiement_mode_display', 'paiement_date',
            'paiement_reference', 'paiement_verifie_at',
            'rdv_dates_proposees', 'rdv_date_confirmee', 'rdv_lieu', 'livraison_date',
            'client_reception_nom', 'client_reception_date',
            'admin_remise_nom', 'admin_remise_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'client', 'created_at', 'updated_at']

    def get_dossier_ref(self, obj):
        return f"MM-{str(obj.dossier_id).zfill(6)}"

    def get_etape_courante(self, obj):
        ordre = ['a_signer', 'signe', 'a_payer', 'paye',
                 'rdv_propose', 'rdv_confirme', 'reception_signee', 'actif']
        try:
            return ordre.index(obj.statut) + 1
        except ValueError:
            return None


class ContratCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Contrat
        fields = ['dossier', 'vehicle', 'type', 'montant',
                  'date_debut', 'date_fin', 'km_initial', 'notes_admin']

    def validate_dossier(self, dossier):
        if dossier.status != 'valide':
            raise serializers.ValidationError('Le dossier doit être validé.')
        if hasattr(dossier, 'contrat'):
            raise serializers.ValidationError('Un contrat existe déjà pour ce dossier.')
        return dossier

    def create(self, validated_data):
        validated_data['client']    = validated_data['dossier'].client
        validated_data['km_actuel'] = validated_data.get('km_initial', 0)
        validated_data['statut']    = 'a_signer'
        return super().create(validated_data)


class ContratKmSerializer(serializers.Serializer):
    km_actuel = serializers.IntegerField(min_value=0)


class ContratSignerSerializer(serializers.Serializer):
    signature_nom = serializers.CharField(max_length=120)


class ContratValiderSignatureSerializer(serializers.Serializer):
    notes_admin = serializers.CharField(required=False, allow_blank=True)
    commentaire = serializers.CharField(required=False, allow_blank=True)


class ContratValiderPaiementSerializer(serializers.Serializer):
    paiement_mode      = serializers.ChoiceField(choices=['virement', 'cb', 'cheque', 'especes'])
    paiement_date      = serializers.DateField()
    paiement_reference = serializers.CharField(required=False, allow_blank=True)
    notes_admin        = serializers.CharField(required=False, allow_blank=True)
    commentaire        = serializers.CharField(required=False, allow_blank=True)


class ContratRDVProposerSerializer(serializers.Serializer):
    rdv_dates_proposees = serializers.ListField(
        child=serializers.DateField(), min_length=1, max_length=5
    )
    rdv_lieu    = serializers.CharField(required=False, allow_blank=True)
    notes_admin = serializers.CharField(required=False, allow_blank=True)
    commentaire = serializers.CharField(required=False, allow_blank=True)


class ContratRDVConfirmerSerializer(serializers.Serializer):
    rdv_date_confirmee = serializers.DateField()


class ContratReceptionSerializer(serializers.Serializer):
    client_reception_nom = serializers.CharField(max_length=200)


class ContratLivrerSerializer(serializers.Serializer):
    livraison_date   = serializers.DateField()
    admin_remise_nom = serializers.CharField(max_length=200)
    notes_admin      = serializers.CharField(required=False, allow_blank=True)
    commentaire      = serializers.CharField(required=False, allow_blank=True)
