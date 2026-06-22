from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenRefreshView
from dossiers.urls import contrat_urlpatterns, sav_urlpatterns


def api_root(request):
    return JsonResponse({
        'name': 'M-Motors API',
        'version': '1.0',
        'endpoints': {
            'auth':      '/api/auth/',
            'vehicles':  '/api/vehicles/',
            'dossiers':  '/api/dossiers/',
            'contrats':  '/api/contrats/',
            'admin':     '/admin/',
        }
    })


urlpatterns = [
    path('', api_root),
    path('api/', api_root),
    path('admin/', admin.site.urls),

    # Auth JWT
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Apps
    path('api/auth/',     include('accounts.urls')),
    path('api/vehicles/', include('vehicles.urls')),
    path('api/dossiers/', include('dossiers.urls')),
    path('api/contrats/', include(contrat_urlpatterns)),
    path('api/sav/',      include(sav_urlpatterns)),
] + [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]

admin.site.site_header = 'M-Motors — Administration'
admin.site.site_title  = 'M-Motors'
admin.site.index_title = 'Tableau de bord'
