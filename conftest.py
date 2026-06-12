import pytest
from rest_framework.test import APIClient
from accounts.models import User
from vehicles.models import Vehicle
from dossiers.models import Dossier


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username='admin@mmotors.fr',
        email='admin@mmotors.fr',
        password='Admin1234!',
        first_name='Admin',
        last_name='MMoto',
        role='admin',
        is_staff=True,
    )


@pytest.fixture
def client_user(db):
    return User.objects.create_user(
        username='client@test.com',
        email='client@test.com',
        password='Client1234!',
        first_name='Jean',
        last_name='Dupont',
        role='client',
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username='other@test.com',
        email='other@test.com',
        password='Other1234!',
        first_name='Marie',
        last_name='Martin',
        role='client',
    )


@pytest.fixture
def admin_client(admin_user):
    c = APIClient()
    c.force_authenticate(user=admin_user)
    c.user = admin_user
    return c


@pytest.fixture
def user_client(client_user):
    c = APIClient()
    c.force_authenticate(user=client_user)
    c.user = client_user
    return c


@pytest.fixture
def other_client(other_user):
    c = APIClient()
    c.force_authenticate(user=other_user)
    c.user = other_user
    return c


@pytest.fixture
def anon_client():
    return APIClient()


@pytest.fixture
def vehicle_achat(db):
    return Vehicle.objects.create(
        brand='Renault', model='Clio', year=2022,
        km=15000, fuel='Essence', type='achat',
        status='disponible', price=12000,
    )


@pytest.fixture
def vehicle_location(db):
    return Vehicle.objects.create(
        brand='Peugeot', model='308', year=2023,
        km=8000, fuel='Diesel', type='location',
        status='disponible', monthly=350,
    )


@pytest.fixture
def dossier(db, client_user, vehicle_achat):
    return Dossier.objects.create(
        client=client_user,
        vehicle=vehicle_achat,
        type='achat',
        status='soumis',
        revenus=2500,
        situation='CDI',
    )
