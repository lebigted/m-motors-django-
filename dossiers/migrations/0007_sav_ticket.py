from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dossiers', '0006_message_model'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SAVTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sujet', models.CharField(max_length=200, verbose_name='Sujet')),
                ('description', models.TextField(verbose_name='Description')),
                ('statut', models.CharField(
                    choices=[
                        ('en_attente', 'En attente de traitement'),
                        ('accepte',    'Suivi ouvert'),
                        ('refuse',     'Non retenu'),
                    ],
                    default='en_attente', max_length=15, verbose_name='Statut',
                )),
                ('reponse', models.TextField(blank=True, verbose_name='Réponse admin')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sav_tickets',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Client',
                )),
            ],
            options={
                'verbose_name': 'Ticket SAV',
                'verbose_name_plural': 'Tickets SAV',
                'ordering': ['-created_at'],
            },
        ),
    ]
