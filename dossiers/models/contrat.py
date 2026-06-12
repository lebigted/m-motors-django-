from django.db import models
from django.conf import settings
from vehicles.models import Vehicle
from .dossier import Dossier


class Contrat(models.Model):
    STATUTS = [
        ('a_signer',         'En attente de signature'),
        ('signe',            'Signé — en attente de paiement'),
        ('a_payer',          'Signature validée — paiement attendu'),
        ('paye',             'Payé — en attente remise'),
        ('rdv_propose',      'RDV remise proposé'),
        ('rdv_confirme',     'RDV remise confirmé'),
        ('reception_signee', 'Véhicule réceptionné — en attente confirmation remise'),
        ('actif',            'Actif — véhicule remis'),
        ('termine',          'Terminé'),
        ('resilie',          'Résilié'),
    ]

    PAIEMENT_MODES = [
        ('virement', 'Virement bancaire'),
        ('cb',       'Carte bancaire'),
        ('cheque',   'Chèque'),
        ('especes',  'Espèces'),
    ]

    dossier  = models.OneToOneField(Dossier, on_delete=models.PROTECT,
                                    related_name='contrat', verbose_name='Dossier')
    client   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                 related_name='contrats', verbose_name='Client')
    vehicle  = models.ForeignKey(Vehicle, on_delete=models.PROTECT,
                                 related_name='contrats', verbose_name='Véhicule')
    type     = models.CharField(max_length=10,
                                choices=[('achat', 'Achat'), ('location', 'Location LLD')],
                                verbose_name='Type')
    montant  = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant (€)')
    date_debut = models.DateField(verbose_name='Date de début')
    date_fin   = models.DateField(null=True, blank=True, verbose_name='Date de fin')
    km_initial = models.PositiveIntegerField(default=0, verbose_name='Km initial')
    km_actuel  = models.PositiveIntegerField(default=0, verbose_name='Km actuel')
    statut     = models.CharField(max_length=20, choices=STATUTS, default='a_signer',
                                  verbose_name='Statut')
    notes_admin = models.TextField(blank=True, verbose_name='Notes internes admin')
    commentaire = models.TextField(blank=True, verbose_name='Message admin → client')

    # Signature
    signature_nom        = models.CharField(max_length=120, blank=True, verbose_name='Nom signataire')
    signature_date       = models.DateTimeField(null=True, blank=True, verbose_name='Date de signature')
    signature_validee_at = models.DateTimeField(null=True, blank=True, verbose_name='Signature validée le')

    # Paiement
    paiement_mode       = models.CharField(max_length=10, choices=PAIEMENT_MODES,
                                           blank=True, verbose_name='Mode de paiement')
    paiement_date       = models.DateField(null=True, blank=True, verbose_name='Date du paiement')
    paiement_reference  = models.CharField(max_length=120, blank=True, verbose_name='Référence paiement')
    paiement_verifie_at = models.DateTimeField(null=True, blank=True, verbose_name='Paiement vérifié le')

    # RDV remise des clés
    rdv_dates_proposees = models.JSONField(default=list, blank=True, verbose_name='Dates RDV proposées')
    rdv_date_confirmee  = models.DateField(null=True, blank=True, verbose_name='Date RDV confirmée')
    rdv_lieu            = models.CharField(max_length=200, blank=True, verbose_name='Lieu de remise')
    livraison_date      = models.DateField(null=True, blank=True, verbose_name='Date de remise effective')

    # Double signature remise
    client_reception_nom  = models.CharField(max_length=200, blank=True,
                                             verbose_name='Signature réception (client)')
    client_reception_date = models.DateTimeField(null=True, blank=True,
                                                 verbose_name='Date signature réception client')
    admin_remise_nom      = models.CharField(max_length=200, blank=True,
                                             verbose_name='Signature remise (admin)')
    admin_remise_date     = models.DateTimeField(null=True, blank=True,
                                                 verbose_name='Date signature remise admin')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label           = 'dossiers'
        verbose_name        = 'Contrat'
        verbose_name_plural = 'Contrats'
        ordering            = ['-created_at']

    def __str__(self):
        return f"Contrat #{self.pk} — {self.client} — {self.vehicle} [{self.statut}]"
