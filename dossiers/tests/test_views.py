import pytest
from dossiers.models import Dossier


LIST_URL = '/api/dossiers/'


def detail_url(pk):
    return f'/api/dossiers/{pk}/'


def decision_url(pk):
    return f'/api/dossiers/{pk}/decision/'


def documents_url(pk):
    return f'/api/dossiers/{pk}/documents/'


# ── CREATE ────────────────────────────────────────────────

@pytest.mark.django_db
def test_create_dossier_achat(user_client, vehicle_achat):
    res = user_client.post(LIST_URL, {
        'vehicle': vehicle_achat.pk,
        'type': 'achat',
        'revenus': '2500.00',
        'situation': 'CDI',
    })
    assert res.status_code == 201
    assert res.data['type'] == 'achat'


@pytest.mark.django_db
def test_create_dossier_location(user_client, vehicle_location):
    res = user_client.post(LIST_URL, {
        'vehicle': vehicle_location.pk,
        'type': 'location',
        'revenus': '3000.00',
        'situation': 'Fonctionnaire',
    })
    assert res.status_code == 201
    assert res.data['type'] == 'location'


@pytest.mark.django_db
def test_create_dossier_requires_auth(anon_client, vehicle_achat):
    res = anon_client.post(LIST_URL, {
        'vehicle': vehicle_achat.pk,
        'type': 'achat',
    })
    assert res.status_code == 401


@pytest.mark.django_db
def test_create_dossier_client_is_set_automatically(user_client, client_user, vehicle_achat):
    res = user_client.post(LIST_URL, {
        'vehicle': vehicle_achat.pk,
        'type': 'achat',
    })
    assert res.status_code == 201
    dossier = Dossier.objects.get(pk=res.data['id'])
    assert dossier.client == client_user


# ── LIST — isolation par client ───────────────────────────

@pytest.mark.django_db
def test_client_sees_only_own_dossiers(user_client, other_client, vehicle_achat):
    user_client.post(LIST_URL, {'vehicle': vehicle_achat.pk, 'type': 'achat'})
    res = other_client.get(LIST_URL)
    assert res.status_code == 200
    assert res.data['count'] == 0


@pytest.mark.django_db
def test_admin_sees_all_dossiers(admin_client, user_client, other_client, vehicle_achat):
    user_client.post(LIST_URL, {'vehicle': vehicle_achat.pk, 'type': 'achat'})
    other_client.post(LIST_URL, {'vehicle': vehicle_achat.pk, 'type': 'achat'})
    res = admin_client.get(LIST_URL)
    assert res.status_code == 200
    assert res.data['count'] == 2


@pytest.mark.django_db
def test_admin_filter_by_status(admin_client, dossier):
    res = admin_client.get(LIST_URL + '?status=soumis')
    assert res.status_code == 200
    assert res.data['count'] == 1

    res2 = admin_client.get(LIST_URL + '?status=valide')
    assert res2.data['count'] == 0


@pytest.mark.django_db
def test_admin_filter_by_type(admin_client, dossier):
    res = admin_client.get(LIST_URL + '?type=achat')
    assert res.data['count'] == 1

    res2 = admin_client.get(LIST_URL + '?type=location')
    assert res2.data['count'] == 0


# ── DECISION ─────────────────────────────────────────────

@pytest.mark.django_db
def test_admin_validate_dossier(admin_client, dossier):
    res = admin_client.patch(decision_url(dossier.pk), {'status': 'valide'})
    assert res.status_code == 200
    assert res.data['status'] == 'valide'
    dossier.refresh_from_db()
    assert dossier.status == 'valide'


@pytest.mark.django_db
def test_admin_refuse_dossier_with_motif(admin_client, dossier):
    res = admin_client.patch(decision_url(dossier.pk), {
        'status': 'refuse',
        'motif': 'Revenus insuffisants pour ce véhicule.',
    })
    assert res.status_code == 200
    assert res.data['status'] == 'refuse'


@pytest.mark.django_db
def test_refuse_without_motif_returns_400(admin_client, dossier):
    res = admin_client.patch(decision_url(dossier.pk), {
        'status': 'refuse',
        'motif': '',
    })
    assert res.status_code == 400
    assert 'motif' in str(res.data)


@pytest.mark.django_db
def test_client_cannot_make_decision(user_client, dossier):
    res = user_client.patch(decision_url(dossier.pk), {'status': 'valide'})
    assert res.status_code == 403


@pytest.mark.django_db
def test_decision_requires_auth(anon_client, dossier):
    res = anon_client.patch(decision_url(dossier.pk), {'status': 'valide'})
    assert res.status_code == 401


# ── DOCUMENTS ─────────────────────────────────────────────

@pytest.mark.django_db
def test_list_documents_returns_empty(user_client, dossier):
    res = user_client.get(documents_url(dossier.pk))
    assert res.status_code == 200
    assert res.data == []


@pytest.mark.django_db
def test_other_client_cannot_access_dossier(other_client, dossier):
    res = other_client.get(detail_url(dossier.pk))
    assert res.status_code == 404
