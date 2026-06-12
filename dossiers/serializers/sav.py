from rest_framework import serializers
from ..models import SAVTicket, SAVMessage
from accounts.serializers import UserSerializer


class SAVTicketSerializer(serializers.ModelSerializer):
    client_info    = UserSerializer(source='client', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model  = SAVTicket
        fields = ['id', 'client', 'client_info', 'sujet', 'description',
                  'statut', 'statut_display', 'reponse', 'created_at', 'updated_at']
        read_only_fields = ['id', 'client', 'statut', 'reponse', 'created_at', 'updated_at']


class SAVTicketCreateSerializer(serializers.Serializer):
    sujet       = serializers.CharField(max_length=200)
    description = serializers.CharField()


class SAVTicketTraiterSerializer(serializers.Serializer):
    statut  = serializers.ChoiceField(choices=['accepte', 'refuse'])
    reponse = serializers.CharField(required=False, allow_blank=True)


class SAVMessageSerializer(serializers.ModelSerializer):
    auteur_nom  = serializers.SerializerMethodField()
    auteur_role = serializers.SerializerMethodField()

    class Meta:
        model  = SAVMessage
        fields = ['id', 'ticket', 'auteur', 'auteur_nom', 'auteur_role', 'contenu', 'created_at']
        read_only_fields = ['id', 'ticket', 'auteur', 'auteur_nom', 'auteur_role', 'created_at']

    def get_auteur_nom(self, obj):
        return f"{obj.auteur.first_name} {obj.auteur.last_name}".strip() or obj.auteur.email

    def get_auteur_role(self, obj):
        return 'admin' if obj.auteur.is_admin else 'client'
