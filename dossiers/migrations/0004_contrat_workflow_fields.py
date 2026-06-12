from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dossiers', '0003_add_archived_field'),
    ]

    operations = [
        # Nouveau statut (max_length 10 → 15 pour rdv_confirme)
        migrations.AlterField(
            model_name='contrat',
            name='statut',
            field=models.CharField(
                max_length=15,
                choices=[
                    ('a_signer',     'En attente de signature'),
                    ('signe',        'Signé — en attente de paiement'),
                    ('a_payer',      'Signature validée — paiement attendu'),
                    ('paye',         'Payé — en attente remise'),
                    ('rdv_propose',  'RDV remise proposé'),
                    ('rdv_confirme', 'RDV remise confirmé'),
                    ('actif',        'Actif — véhicule remis'),
                    ('termine',      'Terminé'),
                    ('resilie',      'Résilié'),
                ],
                default='a_signer',
                verbose_name='Statut',
            ),
        ),

        # Notes admin + commentaire visible client
        migrations.AddField(
            model_name='contrat',
            name='notes_admin',
            field=models.TextField(blank=True, verbose_name='Notes internes admin'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='commentaire',
            field=models.TextField(blank=True, verbose_name='Message admin → client'),
        ),

        # Signature
        migrations.AddField(
            model_name='contrat',
            name='signature_date',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Date de signature'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='signature_validee_at',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Signature validée le'),
        ),

        # Paiement
        migrations.AddField(
            model_name='contrat',
            name='paiement_mode',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('virement', 'Virement bancaire'),
                    ('cb',       'Carte bancaire'),
                    ('cheque',   'Chèque'),
                    ('especes',  'Espèces'),
                ],
                blank=True,
                verbose_name='Mode de paiement',
            ),
        ),
        migrations.AddField(
            model_name='contrat',
            name='paiement_date',
            field=models.DateField(null=True, blank=True, verbose_name='Date du paiement'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='paiement_reference',
            field=models.CharField(max_length=120, blank=True, verbose_name='Référence paiement'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='paiement_verifie_at',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Paiement vérifié le'),
        ),

        # RDV remise
        migrations.AddField(
            model_name='contrat',
            name='rdv_dates_proposees',
            field=models.JSONField(default=list, blank=True, verbose_name='Dates RDV proposées'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='rdv_date_confirmee',
            field=models.DateField(null=True, blank=True, verbose_name='Date RDV confirmée'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='rdv_lieu',
            field=models.CharField(max_length=200, blank=True, verbose_name='Lieu de remise'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='livraison_date',
            field=models.DateField(null=True, blank=True, verbose_name='Date de remise effective'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
