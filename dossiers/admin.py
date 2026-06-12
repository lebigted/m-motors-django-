from django.contrib import admin
from .models import Dossier, Document


class DocumentInline(admin.TabularInline):
    model  = Document
    extra  = 0
    fields = ['type_doc', 'fichier', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display   = ['id', 'client', 'vehicle', 'type', 'status', 'revenus', 'created_at']
    list_filter    = ['status', 'type']
    search_fields  = ['client__email', 'client__last_name', 'vehicle__brand', 'vehicle__model']
    ordering       = ['-created_at']
    readonly_fields = ['client', 'vehicle', 'type', 'created_at', 'updated_at']
    inlines        = [DocumentInline]
    actions        = ['valider', 'refuser', 'mettre_en_cours']

    @admin.action(description='✅ Valider les dossiers sélectionnés')
    def valider(self, request, queryset):
        queryset.update(status='valide')

    @admin.action(description='❌ Refuser les dossiers sélectionnés')
    def refuser(self, request, queryset):
        queryset.update(status='refuse')

    @admin.action(description='🔍 Mettre en cours d\'instruction')
    def mettre_en_cours(self, request, queryset):
        queryset.update(status='en_cours')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display  = ['id', 'dossier', 'type_doc', 'fichier', 'uploaded_at']
    list_filter   = ['type_doc']
    readonly_fields = ['uploaded_at']
