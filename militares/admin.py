from django.contrib import admin


# Register your models here.

from .models import MilitarIncluso, Beneficiario

from .models import TB_Vencimentos

admin.site.register(MilitarIncluso)
admin.site.register(Beneficiario)
admin.site.register(TB_Vencimentos)