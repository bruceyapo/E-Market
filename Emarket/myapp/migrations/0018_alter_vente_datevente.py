# Generated by Django 5.0.3 on 2024-04-17 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_alter_vente_datevente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vente',
            name='DateVente',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]