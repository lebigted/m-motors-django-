from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DossierViewSet, ContratViewSet, SAVTicketViewSet

dossier_router = DefaultRouter()
dossier_router.register('', DossierViewSet, basename='dossier')

contrat_router = DefaultRouter()
contrat_router.register('', ContratViewSet, basename='contrat')

sav_router = DefaultRouter()
sav_router.register('', SAVTicketViewSet, basename='sav')

urlpatterns = [
    path('', include(dossier_router.urls)),
]

contrat_urlpatterns = [
    path('', include(contrat_router.urls)),
]

sav_urlpatterns = [
    path('', include(sav_router.urls)),
]
