# Generated by Django 4.1.3 on 2024-05-15 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0011_tb_vencimentos"),
    ]

    operations = [
        migrations.CreateModel(
            name="MemorialDeCalculo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("protocolo_memorial", models.CharField(max_length=100)),
                ("oficio_dp", models.CharField(max_length=100)),
                ("RE_do_MilitarIncluso", models.CharField(max_length=100)),
                ("posto_graduacao", models.CharField(max_length=100)),
                ("nome_MilitarIncluso", models.CharField(max_length=255)),
                ("data_agregacao", models.DateField()),
                ("mes_referencia", models.CharField(max_length=100)),
                (
                    "salario_padrao",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("retp", models.DecimalField(decimal_places=2, max_digits=10)),
                ("adicionais", models.DecimalField(decimal_places=2, max_digits=10)),
                ("sexta_parte", models.DecimalField(decimal_places=2, max_digits=10)),
                ("hora_aula", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "retp_incorp_hora_aula",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "ats_incorp_hora_aula",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "sexta_parte_incorp_hora_aula",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("outros", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total_bruto", models.DecimalField(decimal_places=2, max_digits=10)),
                ("meses_serem_pagos", models.IntegerField()),
                (
                    "total_empenhado",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "auxilio_reclusao",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("soma_total_pg", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "militar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="militares.militarincluso",
                    ),
                ),
            ],
            options={
                "verbose_name": "Memorial de Cálculo",
                "verbose_name_plural": "Memoriais de Cálculo",
            },
        ),
    ]
