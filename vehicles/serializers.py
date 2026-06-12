from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    type_display   = serializers.CharField(source='get_type_display',   read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    fuel_display   = serializers.CharField(source='get_fuel_display',   read_only=True)

    photo_url = serializers.SerializerMethodField()

    class Meta:
        model  = Vehicle
        fields = [
            'id', 'brand', 'model', 'year', 'km', 'fuel', 'fuel_display',
            'color', 'doors', 'type', 'type_display', 'status', 'status_display',
            'price', 'monthly', 'photo', 'photo_url',
            'svc_assurance', 'svc_assistance', 'svc_entretien', 'svc_ct', 'svc_options',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'photo_url', 'created_at', 'updated_at']

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url
        return None

    def validate(self, data):
        vtype = data.get('type', getattr(self.instance, 'type', None))
        price   = data.get('price',   getattr(self.instance, 'price',   None))
        monthly = data.get('monthly', getattr(self.instance, 'monthly', None))
        if vtype == 'achat' and not price:
            raise serializers.ValidationError({'price': 'Le prix est requis pour un véhicule à vendre.'})
        if vtype == 'location' and not monthly:
            raise serializers.ValidationError({'monthly': 'Le loyer mensuel est requis pour un véhicule en location.'})
        return data
