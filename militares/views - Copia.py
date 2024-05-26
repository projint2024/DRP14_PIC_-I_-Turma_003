from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.urls import reverse
from django.views.generic import UpdateView
from .models import Beneficiario
from .models import MilitarIncluso
import logging
logger = logging.getLogger(__name__)
# views.py

# Importe a classe forms e DateInput
from django import forms
from .forms import MilitarInclusoForm

class DateInput(forms.DateInput):
    input_type = 'date'

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import MilitarIncluso, Beneficiario
from .forms import MilitarInclusoForm
import datetime
from django import forms


class MilitarInclusoForm(forms.ModelForm):
    incluir_hora_aula = forms.BooleanField(label='Incluir hora aula?', required=False)
    incluir_data_saida = forms.BooleanField(label='Incluir Data de Saida?', required=False)

    class Meta:
        model = MilitarIncluso
        fields = ['oficio_dp', 'RE', 'posto_graduacao', 'nome', 'adicionais', 'dependentes', 'sexta_parte', 'hora_aula', 'data_agregacao', 'data_saida', 'mes_referencia', 'pag_a_contar_de']
        widgets = {
            'data_agregacao': DateInput(),
            'data_saida': DateInput(),
            'pag_a_contar_de': DateInput(),
        }

    def clean_data_agregacao(self):
        data_agregacao = self.cleaned_data['data_agregacao']
        if data_agregacao:
            if isinstance(data_agregacao, str):
                try:
                    data_agregacao = datetime.datetime.strptime(data_agregacao, '%d/%m/%Y').date()
                except ValueError:
                    raise forms.ValidationError('Formato de data inválido. Use o formato dd/mm/aaaa.')
            elif not isinstance(data_agregacao, datetime.date):
                raise forms.ValidationError('Tipo de dado inválido para data.')
        return data_agregacao

    def clean_data_saida(self):
        data_saida = self.cleaned_data['data_saida']
        if data_saida:
            if isinstance(data_saida, str):
                try:
                    data_saida = datetime.datetime.strptime(data_saida, '%d/%m/%Y').date()
                except ValueError:
                    raise forms.ValidationError('Formato de data inválido. Use o formato dd/mm/aaaa.')
            elif not isinstance(data_saida, datetime.date):
                raise forms.ValidationError('Tipo de dado inválido para data.')
        return data_saida


class MilitarListView(ListView):
    model = MilitarIncluso
    template_name = 'militar_list.html'
    context_object_name = 'militares'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Consulta para obter a quantidade de militares cadastrados
        total_militares = MilitarIncluso.objects.count()
        # Consulta para obter a quantidade de beneficiários cadastrados
        total_beneficiarios = Beneficiario.objects.count()
        # Adicionando o total de militares e beneficiários ao contexto
        context['total_militares'] = total_militares
        context['total_beneficiarios'] = total_beneficiarios
        return context


class MilitarDetailView(DetailView):
    model = MilitarIncluso
    template_name = 'militar_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        militar = self.get_object()
        context['beneficiarios'] = Beneficiario.objects.filter(militar=militar)
        context['militar'] = militar
        return context


class MilitarCreateView(CreateView):
    model = MilitarIncluso
    form_class = MilitarInclusoForm
    template_name = 'militar_form.html'
    success_url = reverse_lazy('militares:militar_list')

    def form_valid(self, form):
        logger.debug('Formulário válido.')
        return super().form_valid(form)



class MilitarUpdateView(UpdateView):
    model = MilitarIncluso
    fields = '__all__'
    template_name = 'militar_form.html'


class MilitarDeleteView(DeleteView):
    model = MilitarIncluso
    success_url = reverse_lazy('militares:militar_list')
    template_name = 'militar_confirm_delete.html'


class BeneficiarioCreateView(CreateView):
    model = Beneficiario
    fields = '__all__'
    template_name = 'beneficiario_form.html'

    def form_valid(self, form):
        militar = get_object_or_404(MilitarIncluso, pk=self.kwargs['pk'])
        form.instance.militar = militar
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('militares:militar_detail', kwargs={'pk': self.kwargs['pk']})





class BeneficiarioUpdateView(UpdateView):
    model = Beneficiario
    fields = '__all__'  # Ou você pode especificar os campos que deseja editar
    template_name = 'beneficiario_form.html'

    def get_object(self, queryset=None):
        # Obtém o beneficiário com base no ID fornecido na URL
        # e no ID do militar para garantir que esteja associado ao militar correto
        militar_id = self.kwargs.get('pk')  # Obtém o ID do militar da URL
        beneficiario_id = self.kwargs.get('pk_beneficiario')  # Obtém o ID do beneficiário da URL
        beneficiario = get_object_or_404(Beneficiario, pk=beneficiario_id, militar_id=militar_id)
        return beneficiario

    def get_success_url(self):
        # Redireciona para a página de detalhes do militar após a atualização do beneficiário
        return reverse('militares:militar_detail', kwargs={'pk': self.kwargs['pk']})



class BeneficiarioDeleteView(DeleteView):
    model = Beneficiario

    def get_success_url(self):
        return reverse('militares:militar_detail', kwargs={'pk': self.object.militar.pk})


