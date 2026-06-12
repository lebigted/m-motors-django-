import pytest
from accounts.models import User


@pytest.mark.django_db
def test_user_str():
    u = User(first_name='Jean', last_name='Dupont', email='jean@test.com')
    assert str(u) == 'Jean Dupont <jean@test.com>'


@pytest.mark.django_db
def test_is_admin_via_role(admin_user):
    assert admin_user.is_admin is True


@pytest.mark.django_db
def test_is_admin_false_for_client(client_user):
    assert client_user.is_admin is False


@pytest.mark.django_db
def test_is_admin_via_is_staff(db):
    u = User.objects.create_user(
        username='staff@test.com', email='staff@test.com',
        password='pass', role='client', is_staff=True,
    )
    assert u.is_admin is True


@pytest.mark.django_db
def test_email_is_username_field():
    assert User.USERNAME_FIELD == 'email'


@pytest.mark.django_db
def test_default_role_is_client(db):
    u = User.objects.create_user(
        username='new@test.com', email='new@test.com', password='pass',
    )
    assert u.role == 'client'


@pytest.mark.django_db
def test_email_must_be_unique(client_user):
    with pytest.raises(Exception):
        User.objects.create_user(
            username='dup@test.com',
            email=client_user.email,
            password='pass',
        )
