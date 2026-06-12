import pytest
from vehicles.models import Vehicle


@pytest.mark.django_db
def test_vehicle_str(vehicle_achat):
    assert str(vehicle_achat) == 'Renault Clio 2022 (achat)'


@pytest.mark.django_db
def test_toggle_type_achat_to_location(vehicle_achat):
    vehicle_achat.toggle_type()
    assert vehicle_achat.type == 'location'


@pytest.mark.django_db
def test_toggle_type_location_to_achat(vehicle_location):
    vehicle_location.toggle_type()
    assert vehicle_location.type == 'achat'


@pytest.mark.django_db
def test_toggle_type_saves_to_db(vehicle_achat):
    vehicle_achat.toggle_type()
    refreshed = Vehicle.objects.get(pk=vehicle_achat.pk)
    assert refreshed.type == 'location'


@pytest.mark.django_db
def test_default_status_is_disponible(db):
    v = Vehicle.objects.create(
        brand='Toyota', model='Yaris', year=2021,
        km=5000, fuel='Hybride', type='achat', price=15000,
    )
    assert v.status == 'disponible'


@pytest.mark.django_db
def test_default_svc_fields_are_true(vehicle_location):
    assert vehicle_location.svc_assurance is True
    assert vehicle_location.svc_assistance is True
    assert vehicle_location.svc_entretien is True
    assert vehicle_location.svc_ct is True


@pytest.mark.django_db
def test_svc_options_default_empty_list(vehicle_location):
    assert vehicle_location.svc_options == []


@pytest.mark.django_db
def test_vehicle_ordering_newest_first(db):
    Vehicle.objects.create(brand='A', model='1', year=2020, km=0, fuel='Essence', type='achat', price=5000)
    v2 = Vehicle.objects.create(brand='B', model='2', year=2021, km=0, fuel='Essence', type='achat', price=6000)
    vehicles = list(Vehicle.objects.all())
    assert vehicles[0].pk == v2.pk
