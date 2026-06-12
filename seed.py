# -*- coding: utf-8 -*-
"""
Peuple la base de donnees M-Motors avec des donnees de test.
Usage : python seed.py  (apres avoir lance les migrations)
"""
import os
import sys
import django

# Force UTF-8 pour la console Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmotors.settings')
django.setup()

from accounts.models import User  # noqa: E402
from vehicles.models import Vehicle  # noqa: E402
from dossiers.models import Dossier  # noqa: E402

print("[*] Initialisation des donnees M-Motors...")

# -- Utilisateurs ------------------------------------------------------
if not User.objects.filter(email='client@test.com').exists():
    client = User.objects.create_user(
        username='client',
        email='client@test.com',
        password='client123',
        first_name='Jean',
        last_name='Dubois',
        tel='06 12 34 56 78',
        role='client',
    )
    print("  [OK] Client : client@test.com / client123")
else:
    client = User.objects.get(email='client@test.com')
    print("  [--] Client deja existant")

if not User.objects.filter(email='admin@mmotors.fr').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@mmotors.fr',
        password='admin123',
        first_name='Admin',
        last_name='M-Motors',
        role='admin',
    )
    print("  [OK] Admin  : admin@mmotors.fr / admin123")
else:
    admin = User.objects.get(email='admin@mmotors.fr')
    print("  [--] Admin deja existant")

# -- Vehicules ---------------------------------------------------------
vehicles_data = [
    dict(brand='Renault', model='Clio', year=2019, km=45000, fuel='Essence',
         color='Gris', type='achat', status='disponible', price=9500, monthly=None),
    dict(brand='Peugeot', model='308', year=2021, km=28000, fuel='Diesel',
         color='Blanc', type='location', status='disponible', price=None, monthly=320),
    dict(brand='BMW', model='Serie 1', year=2020, km=31000, fuel='Essence',
         color='Noir', type='location', status='disponible', price=None, monthly=520),
    dict(brand='Dacia', model='Sandero', year=2020, km=52000, fuel='Essence',
         color='Bleu', type='achat', status='disponible', price=11500, monthly=None),
    dict(brand='Toyota', model='Yaris', year=2022, km=15000, fuel='Hybride',
         color='Rouge', type='achat', status='disponible', price=14990, monthly=None),
    dict(brand='Volkswagen', model='Golf', year=2019, km=67000, fuel='Diesel',
         color='Argent', type='location', status='disponible', price=None, monthly=280),
    dict(brand='Citroen', model='C3', year=2021, km=22000, fuel='Essence',
         color='Blanc', type='achat', status='reserve', price=12800, monthly=None),
    dict(brand='Ford', model='Focus', year=2020, km=44000, fuel='Diesel',
         color='Gris', type='location', status='disponible', price=None, monthly=310),
]

if Vehicle.objects.count() == 0:
    for v in vehicles_data:
        Vehicle.objects.create(**v)
    print(f"  [OK] {len(vehicles_data)} vehicules crees")
else:
    print(f"  [--] {Vehicle.objects.count()} vehicule(s) deja presents")

# -- Dossier de demonstration ------------------------------------------
if Dossier.objects.count() == 0:
    peugeot = Vehicle.objects.filter(brand='Peugeot').first()
    if peugeot:
        Dossier.objects.create(
            client=client,
            vehicle=peugeot,
            type='location',
            status='en_cours',
            revenus=2800,
            situation='CDI',
            message='Je suis interesse par ce vehicule.',
        )
        print("  [OK] 1 dossier de demonstration cree")
else:
    print(f"  [--] {Dossier.objects.count()} dossier(s) deja presents")

print()
print("[OK] M-Motors pret ! Lancez le serveur avec :")
print("     python manage.py runserver")
print()
print("  Admin Django : http://127.0.0.1:8000/admin/")
print("  API vehicles : http://127.0.0.1:8000/api/vehicles/")
print("  API dossiers : http://127.0.0.1:8000/api/dossiers/")
