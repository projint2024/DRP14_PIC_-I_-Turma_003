# models.py
from django.db import models

class MilitarIncluso(models.Model):
    RE = models.CharField(max_length=6, primary_key=True)

    posto_graduacao = models.CharField(max_length=100, choices=[
        ('Sd PM 2ºCL', 'Sd PM 2ºCL'),
        ('Sd PM 1ºCL', 'Sd PM 1ºCL'),
        ('Cb PM', 'Cb PM'),
        ('3º Sgt PM', '3º Sgt PM'),
        ('2º Sgt PM', '2º Sgt PM'),
        ('1º Sgt PM', '1º Sgt PM'),
        ('SubTen PM', 'SubTen PM'),
        ('Al CFO 1º Ano', 'Al CFO 1º Ano'),
        ('Al CFO 2º Ano', 'Al CFO 2º Ano'),
        ('Al CFO 3º Ano', 'Al CFO 3º Ano'),
        ('Al CFO 4º Ano', 'Al CFO 4º Ano'),
        ('AspTen PM', 'AspTen PM'),
        ('2º Ten PM', '2º Ten PM'),
        ('1º Ten PM', '1º Ten PM'),
        ('Cap Ten PM', 'Cap Ten PM'),
        ('Maj Ten PM', 'Maj Ten PM'),
        ('TenCel PM', 'TenCel PM'),
        ('Cel PM', 'Cel PM'),
    ])


    nome = models.CharField(max_length=255)
    adicionais = models.IntegerField()
    dependentes = models.IntegerField()
    SEXTA_PARTE_CHOICES = [
        ('SIM', 'Sim'),
        ('NAO', 'Não'),
    ]
    sexta_parte = models.CharField(max_length=3, choices=SEXTA_PARTE_CHOICES)
    hora_aula = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    data_agregacao = models.DateField()
    data_saida = models.DateField(null=True, blank=True)
    oficio_dp = models.CharField(max_length=100)
    mes_referencia = models.CharField(max_length=3, choices=[
        ('Jan', 'Janeiro'),
        ('Fev', 'Fevereiro'),
        ('Mar', 'Março'),
        ('Abr', 'Abril'),
        ('Mai', 'Maio'),
        ('Jun', 'Junho'),
        ('Jul', 'Julho'),
        ('Ago', 'Agosto'),
        ('Set', 'Setembro'),
        ('Out', 'Outubro'),
        ('Nov', 'Novembro'),
        ('Dez', 'Dezembro'),
    ])
    pag_a_contar_de = models.DateField()

    def __str__(self):
        return self.RE

class Beneficiario(models.Model):
    militar = models.ForeignKey(MilitarIncluso, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=11, primary_key=True)
    nome = models.CharField(max_length=255)
    agencia_cc = models.CharField(max_length=100)
    cota = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nome

class FinalizadoMilitar(models.Model):
    RE = models.CharField(max_length=6, primary_key=True)
    posto_graduacao = models.CharField(max_length=100)
    nome = models.CharField(max_length=255)
    adicionais = models.IntegerField()
    dependentes = models.IntegerField()
    sexta_parte = models.CharField(max_length=3)
    hora_aula = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    data_agregacao = models.DateField()
    data_saida = models.DateField(null=True, blank=True)
    oficio_dp = models.CharField(max_length=100)
    mes_referencia = models.CharField(max_length=3)
    pag_a_contar_de = models.DateField()

    def __str__(self):
        return self.RE

class FinalizadoBeneficiario(models.Model):
    militar = models.ForeignKey(FinalizadoMilitar, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=11)
    nome = models.CharField(max_length=255)
    agencia_cc = models.CharField(max_length=100)
    cota = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nome

class TB_Vencimentos(models.Model):
    Posto_Grad = models.CharField(max_length=100)
    Codigo = models.CharField(max_length=100)
    Salario_Padrao = models.DecimalField(max_digits=10, decimal_places=2)
    Cod_Funcao = models.CharField(max_length=100)

    def __str__(self):
        return self.Posto_Grad



    class Meta:
        verbose_name = "Memorial de Cálculo"
        verbose_name_plural = "Memoriais de Cálculo"

    def __str__(self):
        return f"Memorial de Cálculo - {self.protocolo_memorial}"

class MemorialDeCalculo(models.Model):
    militar = models.ForeignKey(MilitarIncluso, on_delete=models.CASCADE)
    protocolo_memorial = models.CharField(max_length=100)
    oficio_dp = models.CharField(max_length=100)
    RE_do_MilitarIncluso = models.CharField(max_length=100)
    posto_graduacao = models.CharField(max_length=100)
    nome_MilitarIncluso = models.CharField(max_length=255)
    data_agregacao = models.DateField()
    mes_referencia = models.CharField(max_length=100)
    salario_padrao = models.DecimalField(max_digits=10, decimal_places=2)
    retp = models.DecimalField(max_digits=10, decimal_places=2)
    adicionais = models.DecimalField(max_digits=10, decimal_places=2)
    sexta_parte = models.DecimalField(max_digits=10, decimal_places=2)
    hora_aula = models.DecimalField(max_digits=10, decimal_places=2)
    retp_incorp_hora_aula = models.DecimalField(max_digits=10, decimal_places=2)
    ats_incorp_hora_aula = models.DecimalField(max_digits=10, decimal_places=2)
    sexta_parte_incorp_hora_aula = models.DecimalField(max_digits=10, decimal_places=2)
    outros = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_bruto = models.DecimalField(max_digits=10, decimal_places=2)
    meses_serem_pagos = models.IntegerField()
    total_empenhado = models.DecimalField(max_digits=10, decimal_places=2)
    auxilio_reclusao = models.DecimalField(max_digits=10, decimal_places=2)
    soma_total_pg = models.DecimalField(max_digits=10, decimal_places=2)

class OutrosMemorial(models.Model):
    memorial = models.ForeignKey(MemorialDeCalculo, related_name='outros_campos', on_delete=models.CASCADE)
    nome_campo = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome_campo