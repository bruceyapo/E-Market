# Generated by Django 5.0.3 on 2024-07-12 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commande', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('En attente', 'En attente'), ('Complet', 'Complet')], default='En attente', max_length=15),
        ),
    ]