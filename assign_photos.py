import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mmotors.settings")
django.setup()

from vehicles.models import Vehicle  # noqa: E402

mapping = {
    "Renault":    ("Clio",    "renaultclio.png"),
    "Peugeot":    ("308",     "peugeot308.png"),
    "BMW":        ("Serie 1", "bmwserie1.png"),
    "Dacia":      ("Sandero", "daciasandero.png"),
    "Toyota":     ("Yaris",   "toyotayaris.png"),
    "Volkswagen": ("Golf",    "volkswagengolf.png"),
    "Citroen":    ("C3",      "citroenc3.png"),
    "Ford":       ("Focus",   "fordfocus.png"),
}

for brand, (model, fname) in mapping.items():
    v = Vehicle.objects.filter(brand=brand, model=model).first()
    if v:
        v.photo = f"vehicles/{fname}"
        v.save(update_fields=["photo"])
        print(f"[OK] {brand} {model} -> {fname}")
    else:
        print(f"[!!] Non trouve : {brand} {model}")

total = Vehicle.objects.exclude(photo="").exclude(photo=None).count()
print(f"\nTotal avec photo : {total}/8")
