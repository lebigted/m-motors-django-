from rest_framework import serializers
from ..models import Dossier, Document, Message
from accounts.serializers import UserSerializer
from vehicles.serializers import VehicleSerializer


class DocumentSerializer(serializers.ModelSerializer):
    type_doc_display = serializers.CharField(source='get_type_doc_display', read_only=True)
    fichier_url      = serializers.SerializerMethodField()

    class Meta:
        model  = Document
        fields = ['id', 'dossier', 'type_doc', 'type_doc_display', 'fichier', 'fichier_url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def get_fichier_url(self, obj):
        request = self.context.get('request')
        if obj.fichier and request:
            return request.build_absolute_uri(obj.fichier.url)
        return None


class DossierSerializer(serializers.ModelSerializer):
    documents        = DocumentSerializer(many=True, read_only=True)
    status_display   = serializers.CharField(source='get_status_display', read_only=True)
    type_display     = serializers.CharField(source='get_type_display',   read_only=True)
    client_info      = UserSerializer(source='client', read_only=True)
    vehicle_info     = VehicleSerializer(source='vehicle', read_only=True)
    messages_non_lus = serializers.SerializerMethodField()
    dernier_message  = serializers.SerializerMethodField()

    class Meta:
        model  = Dossier
        fields = [
            'id', 'client', 'client_info', 'vehicle', 'vehicle_info',
            'type', 'type_display', 'status', 'status_display',
            'motif', 'revenus', 'situation', 'message',
            'archived',
            'documents', 'created_at', 'updated_at',
            'messages_non_lus', 'dernier_message',
        ]
        read_only_fields = ['id', 'client', 'status', 'motif', 'archived', 'created_at', 'updated_at']

    def get_messages_non_lus(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        if request.user.is_admin:
            return obj.messages.filter(lu_admin=False).exclude(auteur=request.user).count()
        return obj.messages.filter(lu_client=False).exclude(auteur=request.user).count()

    def get_dernier_message(self, obj):
        msg = obj.messages.last()
        if not msg:
            return None
        return {
            'contenu':     msg.contenu[:80],
            'auteur_role': 'admin' if msg.auteur.is_admin else 'client',
            'created_at':  msg.created_at.isoformat(),
        }


class DossierCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Dossier
        fields = ['id', 'vehicle', 'type', 'revenus', 'situation', 'message']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)


class DossierDecisionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['en_cours', 'valide', 'refuse'])
    motif  = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['status'] == 'refuse' and not data.get('motif', '').strip():
            raise serializers.ValidationError({'motif': 'Un motif est obligatoire pour un refus.'})
        return data


class MessageSerializer(serializers.ModelSerializer):
    auteur_nom  = serializers.SerializerMethodField()
    auteur_role = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = ['id', 'dossier', 'auteur', 'auteur_nom', 'auteur_role',
                  'contenu', 'lu_client', 'lu_admin', 'created_at']
        read_only_fields = ['id', 'auteur', 'lu_client', 'lu_admin', 'created_at']

    def get_auteur_nom(self, obj):
        return f"{obj.auteur.first_name} {obj.auteur.last_name}".strip() or obj.auteur.email

    def get_auteur_role(self, obj):
        return 'admin' if obj.auteur.is_admin else 'client'
