from django.db import models


class Vehicle(models.Model):
    TYPES = [
        ('achat',    'Achat'),
        ('location', 'Location Longue Durée'),
    ]
    STATUSES = [
        ('disponible', 'Disponible'),
        ('reserve',    'Réservé'),
        ('vendu',      'Vendu / Loué'),
    ]
    FUELS = [
        ('Essence',    'Essence'),
        ('Diesel',     'Diesel'),
        ('Hybride',    'Hybride'),
        ('Électrique', 'Électrique'),
    ]

    brand   = models.CharField(max_length=50, verbose_name='Marque')
    model   = models.CharField(max_length=80, verbose_name='Modèle')
    year    = models.PositiveIntegerField(verbose_name='Année')
    km      = models.PositiveIntegerField(default=0, verbose_name='Kilométrage')
    fuel    = models.CharField(max_length=20, choices=FUELS, verbose_name='Carburant')
    color   = models.CharField(max_length=30, blank=True, verbose_name='Couleur')
    doors   = models.PositiveSmallIntegerField(default=5, verbose_name='Portes')
    type    = models.CharField(max_length=10, choices=TYPES, verbose_name='Mode')
    status  = models.CharField(max_length=15, choices=STATUSES, default='disponible', verbose_name='Statut')

    # Prix selon le mode
    price   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Prix achat (€)')
    monthly = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Loyer mensuel (€)'
    )

    photo      = models.ImageField(upload_to='vehicles/', null=True, blank=True, verbose_name='Photo principale')

    # Services inclus (Location LLD uniquement)
    svc_assurance  = models.BooleanField(default=True,  verbose_name='Assurance tous risques incluse')
    svc_assistance = models.BooleanField(default=True,  verbose_name='Assistance dépannage incluse')
    svc_entretien  = models.BooleanField(default=True,  verbose_name='Entretien & SAV inclus')
    svc_ct         = models.BooleanField(default=True,  verbose_name='Contrôle technique inclus')
    # Options supplémentaires : [{"nom": "GPS connecté", "prix": 15}, ...]
    svc_options    = models.JSONField(default=list, blank=True, verbose_name='Options supplémentaires')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Véhicule'
        verbose_name_plural = 'Véhicules'
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.brand} {self.model} {self.year} ({self.type})"

    def toggle_type(self):
        self.type = 'location' if self.type == 'achat' else 'achat'
        self.save()
