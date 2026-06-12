from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.db.models import Count, Q

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Inscription d'un nouveau client."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user   = serializer.save()
    tokens = get_tokens(user)
    return Response({
        **tokens,
        'user': UserSerializer(user).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Connexion — retourne access + refresh + infos user."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user   = serializer.validated_data['user']
    tokens = get_tokens(user)
    return Response({
        **tokens,
        'user': UserSerializer(user).data,
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me(request):
    """Profil de l'utilisateur connecté."""
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)

    serializer = UserSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_list(request):
    """Liste tous les clients avec leurs stats (admin uniquement)."""
    if not request.user.is_admin:
        return Response({'detail': 'Non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

    clients = User.objects.filter(role='client').annotate(
        nb_dossiers=Count('dossiers', distinct=True),
        nb_valides=Count('dossiers', filter=Q(dossiers__status='valide'), distinct=True),
        nb_contrats=Count('contrats', distinct=True),
    ).order_by('-date_joined')

    data = []
    for u in clients:
        d = UserSerializer(u).data
        d['nb_dossiers'] = u.nb_dossiers
        d['nb_valides']  = u.nb_valides
        d['nb_contrats'] = u.nb_contrats
        d['date_joined'] = u.date_joined.isoformat()
        data.append(d)
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Invalide le refresh token."""
    try:
        RefreshToken(request.data['refresh']).blacklist()
    except Exception:
        pass
    return Response({'detail': 'Déconnecté.'})


# ── Réinitialisation du mot de passe ─────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    email = request.data.get('email', '').strip().lower()
    try:
        user = User.objects.get(email=email)
        uid   = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        # En mode DEBUG on renvoie le token pour la démo (pas d'infra email requise)
        if settings.DEBUG:
            return Response({'message': 'Lien généré.', 'uid': uid, 'token': token})
    except User.DoesNotExist:
        pass
    return Response({'message': 'Si un compte existe avec cet email, un lien a été envoyé.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    uid          = request.data.get('uid', '')
    token        = request.data.get('token', '')
    new_password = request.data.get('new_password', '')

    if len(new_password) < 6:
        return Response({'detail': 'Le mot de passe doit faire au moins 6 caractères.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        pk   = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=pk)
    except Exception:
        return Response({'detail': 'Lien invalide ou expiré.'}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({'detail': 'Lien invalide ou expiré.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Mot de passe réinitialisé avec succès.'})
