# Generated by Django 2.2.2 on 2019-06-15 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parsedata', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userpurchase',
            old_name='cpf_invalido',
            new_name='cpf_valido',
        ),
    ]
