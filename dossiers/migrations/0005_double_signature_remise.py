from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dossiers', '0004_contrat_workflow_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contrat',
            name='statut',
            field=models.CharField(
                max_length=20,
                choices=[
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
                ],
                default='a_signer',
                verbose_name='Statut',
            ),
        ),
        migrations.AddField(
            model_name='contrat',
            name='client_reception_nom',
            field=models.CharField(max_length=200, blank=True,
                                   verbose_name='Signature réception (client)'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='client_reception_date',
            field=models.DateTimeField(null=True, blank=True,
                                       verbose_name='Date signature réception client'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='admin_remise_nom',
            field=models.CharField(max_length=200, blank=True,
                                   verbose_name='Signature remise (admin)'),
        ),
        migrations.AddField(
            model_name='contrat',
            name='admin_remise_date',
            field=models.DateTimeField(null=True, blank=True,
                                       verbose_name='Date signature remise admin'),
        ),
    ]
