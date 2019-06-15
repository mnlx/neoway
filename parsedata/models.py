from django.db import models


# Create your models here.
class UserPurchase(models.Model):
    cpf = models.CharField(null=False, max_length=20, unique=True)
    private = models.BooleanField(null=True,)
    incompleto = models.BooleanField(null=True,)
    data_ultima_compra = models.DateField(null=True,)
    ticket_medio = models.FloatField(null=True,)
    ticket_ultima_compra = models.FloatField(null=True,)
    loja_mais_frequente = models.CharField(null=True,max_length=20)
    loja_ultima_compra = models.CharField(null=True,max_length=20)
    cpf_valido = models.BooleanField(null=True)
    cnpj_loja_mais_frequente_valido = models.BooleanField(null=True)
    cnpj_loja_ultima_compra_valido = models.BooleanField(null=True)

