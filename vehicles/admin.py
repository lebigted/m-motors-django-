from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display   = ['brand', 'model', 'year', 'km', 'fuel', 'type', 'status', 'price', 'monthly']
    list_filter    = ['type', 'status', 'fuel', 'brand']
    search_fields  = ['brand', 'model', 'color']
    list_editable  = ['status', 'type']
    ordering       = ['-created_at']
    actions        = ['toggle_to_location', 'toggle_to_achat', 'mark_disponible']

    @admin.action(description='Basculer en Location LLD')
    def toggle_to_location(self, request, queryset):
        queryset.update(type='location')

    @admin.action(description='Basculer en Achat')
    def toggle_to_achat(self, request, queryset):
        queryset.update(type='achat')

    @admin.action(description='Marquer comme disponible')
    def mark_disponible(self, request, queryset):
        queryset.update(status='disponible')
