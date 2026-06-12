from django.urls import path
from . import views

urlpatterns = [
    path('register/',               views.register,                name='auth-register'),
    path('login/',                  views.login,                   name='auth-login'),
    path('logout/',                 views.logout,                  name='auth-logout'),
    path('me/',                     views.me,                      name='auth-me'),
    path('clients/',                views.client_list,             name='auth-clients'),
    path('password-reset/',         views.password_reset_request,  name='auth-password-reset'),
    path('password-reset/confirm/', views.password_reset_confirm,  name='auth-password-reset-confirm'),
]
