from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Vehicle
from .serializers import VehicleSerializer


class IsAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        from rest_framework.permissions import SAFE_METHODS
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_admin


class VehicleViewSet(viewsets.ModelViewSet):
    queryset           = Vehicle.objects.all()
    serializer_class   = VehicleSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['brand', 'model', 'fuel', 'color']
    ordering_fields    = ['year', 'km', 'price', 'monthly', 'created_at']

    def get_queryset(self):
        qs     = super().get_queryset()
        params = self.request.query_params

        if vtype := params.get('type'):
            qs = qs.filter(type=vtype)
        if vstatus := params.get('status'):
            qs = qs.filter(status=vstatus)
        if brand := params.get('brand'):
            qs = qs.filter(brand__icontains=brand)
        if fuel := params.get('fuel'):
            qs = qs.filter(fuel=fuel)
        if max_price := params.get('max_price'):
            qs = qs.filter(price__lte=max_price)
        if max_monthly := params.get('max_monthly'):
            qs = qs.filter(monthly__lte=max_monthly)
        return qs

    @action(detail=True, methods=['patch'], url_path='toggle-type')
    def toggle_type(self, request, pk=None):
        """Bascule un véhicule entre achat et location."""
        vehicle = self.get_object()
        vehicle.toggle_type()
        return Response(VehicleSerializer(vehicle).data)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """Met à jour le statut d'un véhicule (disponible/réservé/vendu)."""
        vehicle = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Vehicle.STATUSES):
            return Response({'detail': 'Statut invalide.'}, status=status.HTTP_400_BAD_REQUEST)
        vehicle.status = new_status
        vehicle.save()
        return Response(VehicleSerializer(vehicle).data)
