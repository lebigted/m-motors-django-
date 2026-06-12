import pytest
from dossiers.models import Dossier, Document


@pytest.mark.django_db
def test_dossier_str(dossier, client_user, vehicle_achat):
    expected = f'Dossier #{dossier.pk} — {client_user} — {vehicle_achat} [soumis]'
    assert str(dossier) == expected


@pytest.mark.django_db
def test_dossier_default_status_is_soumis(db, client_user, vehicle_achat):
    d = Dossier.objects.create(
        client=client_user, vehicle=vehicle_achat, type='achat',
    )
    assert d.status == 'soumis'


@pytest.mark.django_db
def test_dossier_ordering_newest_first(db, client_user, vehicle_achat):
    Dossier.objects.create(client=client_user, vehicle=vehicle_achat, type='achat')
    d2 = Dossier.objects.create(client=client_user, vehicle=vehicle_achat, type='location')
    dossiers = list(Dossier.objects.all())
    assert dossiers[0].pk == d2.pk


@pytest.mark.django_db
def test_document_str(db, dossier):
    doc = Document(dossier=dossier, type_doc='cni')
    assert "Pièce d'identité" in str(doc)
    assert str(dossier.pk) in str(doc)
