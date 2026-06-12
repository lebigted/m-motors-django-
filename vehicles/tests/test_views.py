import pytest
from vehicles.models import Vehicle


LIST_URL = '/api/vehicles/'


def detail_url(pk):
    return f'/api/vehicles/{pk}/'


def toggle_url(pk):
    return f'/api/vehicles/{pk}/toggle-type/'


def status_url(pk):
    return f'/api/vehicles/{pk}/status/'


# ── LIST / RETRIEVE — accès public ───────────────────────

@pytest.mark.django_db
def test_list_vehicles_public(anon_client, vehicle_achat, vehicle_location):
    res = anon_client.get(LIST_URL)
    assert res.status_code == 200
    assert res.data['count'] == 2


@pytest.mark.django_db
def test_retrieve_vehicle_public(anon_client, vehicle_achat):
    res = anon_client.get(detail_url(vehicle_achat.pk))
    assert res.status_code == 200
    assert res.data['brand'] == 'Renault'


# ── FILTRES ───────────────────────────────────────────────

@pytest.mark.django_db
def test_filter_by_type_achat(anon_client, vehicle_achat, vehicle_location):
    res = anon_client.get(LIST_URL + '?type=achat')
    assert res.status_code == 200
    assert res.data['count'] == 1
    assert res.data['results'][0]['type'] == 'achat'


@pytest.mark.django_db
def test_filter_by_type_location(anon_client, vehicle_achat, vehicle_location):
    res = anon_client.get(LIST_URL + '?type=location')
    assert res.status_code == 200
    assert res.data['count'] == 1
    assert res.data['results'][0]['type'] == 'location'


@pytest.mark.django_db
def test_filter_by_fuel(anon_client, vehicle_achat, vehicle_location):
    res = anon_client.get(LIST_URL + '?fuel=Essence')
    assert res.status_code == 200
    assert all(v['fuel'] == 'Essence' for v in res.data['results'])


@pytest.mark.django_db
def test_filter_by_max_price(anon_client, vehicle_achat):
    res = anon_client.get(LIST_URL + '?max_price=15000')
    assert res.status_code == 200
    assert res.data['count'] == 1

    res2 = anon_client.get(LIST_URL + '?max_price=5000')
    assert res2.data['count'] == 0


@pytest.mark.django_db
def test_filter_by_status(anon_client, vehicle_achat):
    res = anon_client.get(LIST_URL + '?status=disponible')
    assert res.status_code == 200
    assert res.data['count'] == 1


# ── CREATE — admin uniquement ─────────────────────────────

@pytest.mark.django_db
def test_create_vehicle_admin_success(admin_client):
    data = {
        'brand': 'BMW', 'model': 'Serie 1', 'year': 2023,
        'km': 5000, 'fuel': 'Essence', 'type': 'achat',
        'status': 'disponible', 'price': '25000.00',
    }
    res = admin_client.post(LIST_URL, data)
    assert res.status_code == 201
    assert res.data['brand'] == 'BMW'


@pytest.mark.django_db
def test_create_vehicle_client_forbidden(user_client):
    data = {
        'brand': 'BMW', 'model': 'Serie 1', 'year': 2023,
        'km': 5000, 'fuel': 'Essence', 'type': 'achat',
        'status': 'disponible', 'price': '25000.00',
    }
    res = user_client.post(LIST_URL, data)
    assert res.status_code == 403


@pytest.mark.django_db
def test_create_vehicle_anon_requires_auth(anon_client):
    res = anon_client.post(LIST_URL, {'brand': 'BMW'})
    assert res.status_code == 401


@pytest.mark.django_db
def test_create_achat_requires_price(admin_client):
    data = {
        'brand': 'BMW', 'model': 'X1', 'year': 2022,
        'km': 0, 'fuel': 'Diesel', 'type': 'achat', 'status': 'disponible',
    }
    res = admin_client.post(LIST_URL, data)
    assert res.status_code == 400
    assert 'price' in str(res.data)


@pytest.mark.django_db
def test_create_location_requires_monthly(admin_client):
    data = {
        'brand': 'BMW', 'model': 'X1', 'year': 2022,
        'km': 0, 'fuel': 'Diesel', 'type': 'location', 'status': 'disponible',
    }
    res = admin_client.post(LIST_URL, data)
    assert res.status_code == 400
    assert 'monthly' in str(res.data)


# ── UPDATE / DELETE ───────────────────────────────────────

@pytest.mark.django_db
def test_update_vehicle_admin(admin_client, vehicle_achat):
    res = admin_client.patch(detail_url(vehicle_achat.pk), {'km': 20000})
    assert res.status_code == 200
    assert res.data['km'] == 20000


@pytest.mark.django_db
def test_delete_vehicle_admin(admin_client, vehicle_achat):
    res = admin_client.delete(detail_url(vehicle_achat.pk))
    assert res.status_code == 204
    assert not Vehicle.objects.filter(pk=vehicle_achat.pk).exists()


@pytest.mark.django_db
def test_delete_vehicle_client_forbidden(user_client, vehicle_achat):
    res = user_client.delete(detail_url(vehicle_achat.pk))
    assert res.status_code == 403


# ── TOGGLE TYPE ───────────────────────────────────────────

@pytest.mark.django_db
def test_toggle_type_achat_to_location(admin_client, vehicle_achat):
    res = admin_client.patch(toggle_url(vehicle_achat.pk))
    assert res.status_code == 200
    assert res.data['type'] == 'location'


@pytest.mark.django_db
def test_toggle_type_location_to_achat(admin_client, vehicle_location):
    res = admin_client.patch(toggle_url(vehicle_location.pk))
    assert res.status_code == 200
    assert res.data['type'] == 'achat'


@pytest.mark.django_db
def test_toggle_type_client_forbidden(user_client, vehicle_achat):
    res = user_client.patch(toggle_url(vehicle_achat.pk))
    assert res.status_code == 403


# ── UPDATE STATUS ─────────────────────────────────────────

@pytest.mark.django_db
def test_update_status_admin(admin_client, vehicle_achat):
    res = admin_client.patch(status_url(vehicle_achat.pk), {'status': 'reserve'})
    assert res.status_code == 200
    assert res.data['status'] == 'reserve'


@pytest.mark.django_db
def test_update_status_invalid(admin_client, vehicle_achat):
    res = admin_client.patch(status_url(vehicle_achat.pk), {'status': 'invalide'})
    assert res.status_code == 400
