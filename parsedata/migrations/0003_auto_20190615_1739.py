# Generated by Django 2.2.2 on 2019-06-15 17:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parsedata', '0002_auto_20190615_1738'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userpurchase',
            old_name='loja_mais_frequente_valida',
            new_name='cnpj_loja_mais_frequente_valida',
        ),
        migrations.RenameField(
            model_name='userpurchase',
            old_name='loja_ultima_compra_valida',
            new_name='cnpj_loja_ultima_compra_valida',
        ),
    ]
