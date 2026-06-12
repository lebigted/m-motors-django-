import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


REGISTER_URL       = '/api/auth/register/'
LOGIN_URL          = '/api/auth/login/'
ME_URL             = '/api/auth/me/'
LOGOUT_URL         = '/api/auth/logout/'
CLIENTS_URL        = '/api/auth/clients/'
PWD_RESET_URL      = '/api/auth/password-reset/'
PWD_CONFIRM_URL    = '/api/auth/password-reset/confirm/'


# ── REGISTER ─────────────────────────────────────────────

@pytest.mark.django_db
def test_register_success(anon_client):
    data = {
        'email': 'nouveau@test.com',
        'first_name': 'Paul',
        'last_name': 'Martin',
        'password': 'Secure123',
        'password2': 'Secure123',
    }
    res = anon_client.post(REGISTER_URL, data)
    assert res.status_code == 201
    assert 'access' in res.data
    assert 'refresh' in res.data
    assert res.data['user']['email'] == 'nouveau@test.com'


@pytest.mark.django_db
def test_register_password_mismatch(anon_client):
    data = {
        'email': 'test@test.com',
        'first_name': 'A',
        'last_name': 'B',
        'password': 'abc123',
        'password2': 'xyz999',
    }
    res = anon_client.post(REGISTER_URL, data)
    assert res.status_code == 400
    assert 'password2' in str(res.data)


@pytest.mark.django_db
def test_register_duplicate_email(client_user, anon_client):
    data = {
        'email': client_user.email,
        'first_name': 'X',
        'last_name': 'Y',
        'password': 'abc123',
        'password2': 'abc123',
    }
    res = anon_client.post(REGISTER_URL, data)
    assert res.status_code == 400


@pytest.mark.django_db
def test_register_missing_field(anon_client):
    res = anon_client.post(REGISTER_URL, {'email': 'x@test.com'})
    assert res.status_code == 400


# ── LOGIN ─────────────────────────────────────────────────

@pytest.mark.django_db
def test_login_success(client_user, anon_client):
    res = anon_client.post(LOGIN_URL, {
        'email': client_user.email,
        'password': 'Client1234!',
    })
    assert res.status_code == 200
    assert 'access' in res.data
    assert 'refresh' in res.data


@pytest.mark.django_db
def test_login_wrong_password(client_user, anon_client):
    res = anon_client.post(LOGIN_URL, {
        'email': client_user.email,
        'password': 'mauvaismdp',
    })
    assert res.status_code == 400


@pytest.mark.django_db
def test_login_unknown_email(anon_client):
    res = anon_client.post(LOGIN_URL, {
        'email': 'inconnu@test.com',
        'password': 'n importe',
    })
    assert res.status_code == 400


# ── ME ────────────────────────────────────────────────────

@pytest.mark.django_db
def test_me_get_authenticated(user_client, client_user):
    res = user_client.get(ME_URL)
    assert res.status_code == 200
    assert res.data['email'] == client_user.email
    assert res.data['role'] == 'client'


@pytest.mark.django_db
def test_me_requires_auth(anon_client):
    res = anon_client.get(ME_URL)
    assert res.status_code == 401


@pytest.mark.django_db
def test_me_patch_updates_profile(user_client):
    res = user_client.patch(ME_URL, {'first_name': 'Nouveau'})
    assert res.status_code == 200
    assert res.data['first_name'] == 'Nouveau'


@pytest.mark.django_db
def test_me_cannot_change_role(user_client):
    res = user_client.patch(ME_URL, {'role': 'admin'})
    assert res.status_code == 200
    assert res.data['role'] == 'client'


# ── LOGOUT ───────────────────────────────────────────────

@pytest.mark.django_db
def test_logout_requires_auth(anon_client):
    res = anon_client.post(LOGOUT_URL, {'refresh': 'faketoken'})
    assert res.status_code == 401


@pytest.mark.django_db
def test_logout_success(user_client):
    res = user_client.post(LOGOUT_URL, {'refresh': 'anytoken'})
    assert res.status_code == 200


# ── CLIENT LIST ───────────────────────────────────────────

@pytest.mark.django_db
def test_client_list_as_admin(admin_client):
    res = admin_client.get(CLIENTS_URL)
    assert res.status_code == 200
    assert isinstance(res.data, list)


@pytest.mark.django_db
def test_client_list_forbidden_for_client(user_client):
    res = user_client.get(CLIENTS_URL)
    assert res.status_code == 403


# ── PASSWORD RESET ────────────────────────────────────────

@pytest.mark.django_db
def test_password_reset_request_unknown_email(anon_client):
    res = anon_client.post(PWD_RESET_URL, {'email': 'inconnu@example.com'})
    assert res.status_code == 200
    assert 'message' in res.data


@pytest.mark.django_db
def test_password_reset_request_known_email(anon_client, client_user):
    res = anon_client.post(PWD_RESET_URL, {'email': client_user.email})
    assert res.status_code == 200
    assert 'uid' in res.data
    assert 'token' in res.data


@pytest.mark.django_db
def test_password_reset_confirm_success(anon_client, client_user):
    uid   = urlsafe_base64_encode(force_bytes(client_user.pk))
    token = default_token_generator.make_token(client_user)
    res   = anon_client.post(PWD_CONFIRM_URL, {
        'uid': uid, 'token': token, 'new_password': 'NewPass123!',
    })
    assert res.status_code == 200
    assert 'message' in res.data


@pytest.mark.django_db
def test_password_reset_confirm_short_password(anon_client, client_user):
    uid   = urlsafe_base64_encode(force_bytes(client_user.pk))
    token = default_token_generator.make_token(client_user)
    res   = anon_client.post(PWD_CONFIRM_URL, {
        'uid': uid, 'token': token, 'new_password': '123',
    })
    assert res.status_code == 400


@pytest.mark.django_db
def test_password_reset_confirm_invalid_token(anon_client, client_user):
    uid = urlsafe_base64_encode(force_bytes(client_user.pk))
    res = anon_client.post(PWD_CONFIRM_URL, {
        'uid': uid, 'token': 'badtoken', 'new_password': 'NewPass123!',
    })
    assert res.status_code == 400


@pytest.mark.django_db
def test_password_reset_confirm_invalid_uid(anon_client):
    res = anon_client.post(PWD_CONFIRM_URL, {
        'uid': 'notvalid', 'token': 'anytoken', 'new_password': 'NewPass123!',
    })
    assert res.status_code == 400
