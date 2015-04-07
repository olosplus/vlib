# -*- coding: utf-8 -*-
from django.db import models
#from cadastro.unidade.models import Unidade
from cadastro.empresa.models import Empresa

# Create your models here.
class Master(models.Model):
	"""docstring for ClassName"""
	class Meta:
		db_table = "master"

	id = models.AutoField(primary_key=True,verbose_name="Código", editable=False)
	empresa = models.ForeignKey(Empresa,verbose_name="Empresa")

#class Master_unidade(models.Model):
#    unidade = models.ForeignKey(Unidade,verbose_name="Unidade")

#class Movimentacao(models.Model):
#	"""docstring for ClassName"""
#	class Meta:
#		db_table = "movimentacao"
#
#	id = models.AutoField(primary_key=True,verbose_name="Código")