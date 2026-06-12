from django.db import models
from django.conf import settings


class SAVTicket(models.Model):
    STATUTS = [
        ('en_attente', 'En attente de traitement'),
        ('accepte',    'Suivi ouvert'),
        ('refuse',     'Non retenu'),
        ('cloture',    'Clôturé'),
    ]

    client      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name='sav_tickets', verbose_name='Client')
    sujet       = models.CharField(max_length=200, verbose_name='Sujet')
    description = models.TextField(verbose_name='Description')
    statut      = models.CharField(max_length=15, choices=STATUTS, default='en_attente',
                                   verbose_name='Statut')
    reponse     = models.TextField(blank=True, verbose_name='Réponse admin')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        app_label           = 'dossiers'
        verbose_name        = 'Ticket SAV'
        verbose_name_plural = 'Tickets SAV'
        ordering            = ['-created_at']

    def __str__(self):
        return f"SAV #{self.pk} — {self.client} — {self.sujet} [{self.statut}]"


class SAVMessage(models.Model):
    ticket     = models.ForeignKey(SAVTicket, on_delete=models.CASCADE,
                                   related_name='sav_messages', verbose_name='Ticket SAV')
    auteur     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='sav_messages', verbose_name='Auteur')
    contenu    = models.TextField(verbose_name='Contenu')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label           = 'dossiers'
        verbose_name        = 'Message SAV'
        verbose_name_plural = 'Messages SAV'
        ordering            = ['created_at']

    def __str__(self):
        return f"SAV msg #{self.pk} — ticket #{self.ticket_id} — {self.auteur}"
