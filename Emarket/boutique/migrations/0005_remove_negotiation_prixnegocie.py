# Generated by Django 5.0.3 on 2024-07-14 05:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boutique', '0004_rename_client_negotiation_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='negotiation',
            name='PrixNegocie',
        ),
    ]
