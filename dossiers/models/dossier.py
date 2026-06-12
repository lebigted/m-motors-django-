from django.db import models
from django.conf import settings
from vehicles.models import Vehicle


class Dossier(models.Model):
    TYPES = [
        ('achat',    'Achat'),
        ('location', 'Location LLD'),
    ]
    STATUSES = [
        ('soumis',   'Soumis'),
        ('en_cours', "En cours d'instruction"),
        ('valide',   'Validé'),
        ('refuse',   'Refusé'),
    ]

    client    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='dossiers', verbose_name='Client')
    vehicle   = models.ForeignKey(Vehicle, on_delete=models.PROTECT,
                                  related_name='dossiers', verbose_name='Véhicule')
    type      = models.CharField(max_length=10, choices=TYPES, verbose_name='Type de dossier')
    status    = models.CharField(max_length=10, choices=STATUSES, default='soumis', verbose_name='Statut')
    motif     = models.TextField(blank=True, verbose_name='Motif / Commentaire gestionnaire')
    revenus   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    verbose_name='Revenus nets/mois (€)')
    situation = models.CharField(max_length=50, blank=True, verbose_name='Situation professionnelle')
    message   = models.TextField(blank=True, verbose_name='Message du client')
    archived  = models.BooleanField(default=False, verbose_name='Archivé')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label           = 'dossiers'
        verbose_name        = 'Dossier'
        verbose_name_plural = 'Dossiers'
        ordering            = ['-created_at']

    def __str__(self):
        return f"Dossier #{self.pk} — {self.client} — {self.vehicle} [{self.status}]"


class Document(models.Model):
    TYPE_CHOICES = [
        ('cni',     "Pièce d'identité"),
        ('permis',  'Permis de conduire'),
        ('revenus', 'Justificatif de revenus'),
        ('rib',     'RIB'),
        ('autre',   'Autre'),
    ]

    dossier     = models.ForeignKey(Dossier, on_delete=models.CASCADE,
                                    related_name='documents', verbose_name='Dossier')
    type_doc    = models.CharField(max_length=15, choices=TYPE_CHOICES, verbose_name='Type de document')
    fichier     = models.FileField(upload_to='dossiers/%Y/%m/', verbose_name='Fichier')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label           = 'dossiers'
        verbose_name        = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return f"{self.get_type_doc_display()} — Dossier #{self.dossier_id}"


class Message(models.Model):
    dossier    = models.ForeignKey(Dossier, on_delete=models.CASCADE,
                                   related_name='messages', verbose_name='Dossier')
    auteur     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='messages', verbose_name='Auteur')
    contenu    = models.TextField(verbose_name='Contenu')
    lu_client  = models.BooleanField(default=False, verbose_name='Lu par le client')
    lu_admin   = models.BooleanField(default=False, verbose_name="Lu par l'admin")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label           = 'dossiers'
        verbose_name        = 'Message'
        verbose_name_plural = 'Messages'
        ordering            = ['created_at']

    def __str__(self):
        return f"Message #{self.pk} — Dossier #{self.dossier_id} — {self.auteur}"
