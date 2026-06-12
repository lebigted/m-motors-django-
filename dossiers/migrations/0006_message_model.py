from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dossiers', '0005_double_signature_remise'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenu',    models.TextField(verbose_name='Contenu')),
                ('lu_client',  models.BooleanField(default=False, verbose_name='Lu par le client')),
                ('lu_admin',   models.BooleanField(default=False, verbose_name="Lu par l'admin")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('auteur',     models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                  related_name='messages',
                                                  to=settings.AUTH_USER_MODEL,
                                                  verbose_name='Auteur')),
                ('dossier',    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                  related_name='messages',
                                                  to='dossiers.dossier',
                                                  verbose_name='Dossier')),
            ],
            options={
                'verbose_name':        'Message',
                'verbose_name_plural': 'Messages',
                'ordering':            ['created_at'],
            },
        ),
    ]
