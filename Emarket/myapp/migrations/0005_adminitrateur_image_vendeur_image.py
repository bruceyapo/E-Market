# Generated by Django 5.0.3 on 2024-03-28 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_categorieproduit_adminitrateur_produit_stock_vendeur_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminitrateur',
            name='image',
            field=models.ImageField(default='app/img/default_profil.png', upload_to='Admin'),
        ),
        migrations.AddField(
            model_name='vendeur',
            name='image',
            field=models.ImageField(default='app/img/default_profil.png', upload_to='Vendeur'),
        ),
    ]