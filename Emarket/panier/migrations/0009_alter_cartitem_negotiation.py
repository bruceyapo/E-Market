# Generated by Django 5.0.3 on 2024-07-14 06:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boutique', '0005_remove_negotiation_prixnegocie'),
        ('panier', '0008_alter_cartitem_cart_alter_cartitem_negotiation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='negotiation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='boutique.negotiation'),
        ),
    ]
