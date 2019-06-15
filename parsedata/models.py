from django.db import models


# Create your models here.
class UserPurchase(models.Model):
    cpf = models.CharField(max_length=15)
    private = models.BooleanField()
    incompleto = models.BooleanField()
    data_ultima_compra = models.DateField()
    ticket_medio = models.FloatField()
    ticket_ultima_compra = models.FloatField()
    loja_mais_frequente = models.CharField(max_length=18)
    loja_ultima_compra = models.CharField(max_length=18)
    cpf_invalido = models.BooleanField()
