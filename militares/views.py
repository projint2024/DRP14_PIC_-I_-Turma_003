from django.views import View
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Beneficiario, MilitarIncluso, FinalizadoMilitar, FinalizadoBeneficiario, TB_Vencimentos, MemorialDeCalculo, OutrosMemorial, FinalizadoMilitar, FinalizadoBeneficiario
from .forms import MilitarInclusoForm, TBVencimentosForm, MemorialDeCalculoForm, OutrosMemorialForm
import logging
import datetime
from django import forms

logger = logging.getLogger(__name__)

class DateInput(forms.DateInput):
    input_type = 'date'

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
        total_militares = MilitarIncluso.objects.count()
        total_beneficiarios = Beneficiario.objects.count()
        context['total_militares'] = total_militares
        context['total_beneficiarios'] = total_beneficiarios

        total_MilitarFinalizado = FinalizadoMilitar.objects.count()
        context['total_MilitarFinalizado'] = total_MilitarFinalizado

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
    fields = '__all__'
    template_name = 'beneficiario_form.html'

    def get_object(self, queryset=None):
        militar_id = self.kwargs.get('pk')
        beneficiario_id = self.kwargs.get('pk_beneficiario')
        beneficiario = get_object_or_404(Beneficiario, pk=beneficiario_id, militar_id=militar_id)
        return beneficiario

    def get_success_url(self):
        return reverse('militares:militar_detail', kwargs={'pk': self.kwargs['pk']})

class BeneficiarioDeleteView(DeleteView):
    model = Beneficiario

    def get_success_url(self):
        return reverse('militares:militar_detail', kwargs={'pk': self.object.militar.pk})

def mover_para_finalizados(request, pk):
    militar = get_object_or_404(MilitarIncluso, pk=pk)
    beneficiarios = Beneficiario.objects.filter(militar=militar)

    # Criar e salvar instância de FinalizadoMilitar
    finalizado_militar = FinalizadoMilitar.objects.create(
        RE=militar.RE,
        posto_graduacao=militar.posto_graduacao,
        nome=militar.nome,
        adicionais=militar.adicionais,
        dependentes=militar.dependentes,
        sexta_parte=militar.sexta_parte,
        hora_aula=militar.hora_aula,
        data_agregacao=militar.data_agregacao,
        data_saida=militar.data_saida,
        oficio_dp=militar.oficio_dp,
        mes_referencia=militar.mes_referencia,
        pag_a_contar_de=militar.pag_a_contar_de
    )

    # Criar e salvar instâncias de FinalizadoBeneficiario
    for beneficiario in beneficiarios:
        FinalizadoBeneficiario.objects.create(
            militar=finalizado_militar,
            cpf=beneficiario.cpf,
            nome=beneficiario.nome,
            agencia_cc=beneficiario.agencia_cc,
            cota=beneficiario.cota
        )

    # Remover militar e beneficiários do banco de dados original
    militar.delete()
    beneficiarios.delete()

    return redirect('militares:militar_list')

def view_tb_vencimentos(request):
    tb_vencimentos = TB_Vencimentos.objects.all()
    return render(request, 'view_tb_vencimentos.html', {'tb_vencimentos': tb_vencimentos})

from django.http import JsonResponse

def editar_valor_tb_vencimentos(request):
    if request.method == 'POST':
        data = request.POST
        id = data.get('id')
        campo = data.get('campo')
        novo_valor = data.get('novo_valor')

        # Aqui você precisa adicionar o código para atualizar o valor no banco de dados
        # Supondo que você tenha um modelo TB_Vencimentos com campos correspondentes
        try:
            item = TB_Vencimentos.objects.get(pk=id)
            if campo == 'Posto_Grad':
                item.Posto_Grad = novo_valor
            elif campo == 'Codigo':
                item.Codigo = novo_valor
            elif campo == 'Salario_Padrao':
                item.Salario_Padrao = novo_valor
            elif campo == 'Cod_Funcao':
                item.Cod_Funcao = novo_valor
            item.save()
            return JsonResponse({'status': 'success'})
        except TB_Vencimentos.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item não encontrado'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método não permitido'})

def edit_tb_vencimento(request, codigo):
    tb_vencimento = get_object_or_404(TB_Vencimentos, Codigo=codigo)
    form = TBVencimentosForm(request.POST or None, instance=tb_vencimento)
    if form.is_valid():
        form.save()
        return redirect('view_tb_vencimentos')
    return render(request, 'edit_tb_vencimento.html', {'form': form})




def militar_detail(request, pk):
    militar = get_object_or_404(MilitarIncluso, pk=pk)
    MemorialFormSet = modelformset_factory(MemorialDeCalculo, form=MemorialDeCalculoForm, extra=1)

    if request.method == 'POST':
        formset = MemorialFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.militar = militar
                instance.save()
            return redirect('militares:militar_detail', pk=pk)
    else:
        formset = MemorialFormSet(queryset=MemorialDeCalculo.objects.none())

    return render(request, 'militar_detail.html', {'militar': militar, 'memorial_formset': formset})



class ListaMemoriaisView(ListView):
    model = MemorialDeCalculo
    template_name = 'lista_memoriais.html'
    context_object_name = 'memoriais'

class DetalhesMemorialView(DetailView):
    model = MemorialDeCalculo
    template_name = 'detalhes_memorial.html'
    context_object_name = 'memorial'

class EditarMemorialView(UpdateView):
    model = MemorialDeCalculo
    template_name = 'editar_memorial.html'
    fields = '__all__'

class CriarMemorialView(CreateView):
    model = MemorialDeCalculo
    template_name = 'criar_memorial.html'
    form_class = MemorialDeCalculoForm

    def get_initial(self):
        RE_do_MilitarIncluso = self.request.POST.get('RE_do_MilitarIncluso')
        initial = super().get_initial()
        if RE_do_MilitarIncluso:
            militar = MilitarIncluso.objects.get(RE=RE_do_MilitarIncluso)
            tb_vencimento = TB_Vencimentos.objects.filter(Posto_Grad=militar.posto_graduacao).first()
            if tb_vencimento:
                initial['salario_padrao'] = tb_vencimento.Salario_Padrao
        return initial

def tela_memorial(request):
    memoriais = MemorialDeCalculo.objects.all()
    form = MemorialDeCalculoForm()  # Se você tiver um formulário para criar memorial
    return render(request, 'tela_memorial.html', {'memoriais': memoriais, 'form': form})

def detalhes_militar(request, pk):
    militar = MilitarIncluso.objects.get(pk=pk)
    memoriais = MemorialDeCalculo.objects.filter(militar=militar)

    # Inicialize o salario_padrao como None
    salario_padrao = None

    # Recupere todos os registros de TB_Vencimentos
    tb_vencimentos = TB_Vencimentos.objects.all()

    # Itere sobre os registros para encontrar a correspondência de posto_graduacao
    for item in tb_vencimentos:
        if militar.posto_graduacao == item.Posto_Grad:
            salario_padrao = item.Salario_Padrao
            break  # Se encontrar a correspondência, pare a iteração

    # Verifique se o salario_padrao foi preenchido
    if salario_padrao is not None:
        # Faça o que deseja com o salario_padrao (por exemplo, atribua-o ao contexto)
        context = {
            'militar': militar,
            'memoriais': memoriais,
            'salario_padrao': salario_padrao,
            # Adicione os outros valores ao contexto conforme necessário
        }
    else:
        # Caso não encontre correspondência, você pode definir um valor padrão ou fazer outra ação
        context = {
            'militar': militar,
            'memoriais': memoriais,
            'salario_padrao': "Valor não encontrado",  # Ou qualquer valor padrão que desejar
            # Adicione os outros valores ao contexto conforme necessário
        }

    return render(request, 'militar_detail.html', context)



def criar_memorial(request, militar_id):
    militar = get_object_or_404(MilitarIncluso, id=militar_id)

    MemorialFormSet = modelformset_factory(MemorialDeCalculo, form=MemorialDeCalculoForm, extra=1)
    OutrosMemorialFormSet = modelformset_factory(OutrosMemorial, form=OutrosMemorialForm, extra=1)

    if request.method == 'POST':
        memorial_formset = MemorialFormSet(request.POST, prefix='memorial')
        outros_memorial_formset = OutrosMemorialFormSet(request.POST, prefix='outros')

        if memorial_formset.is_valid() and outros_memorial_formset.is_valid():
            memorial_instances = memorial_formset.save(commit=False)
            for instance in memorial_instances:
                instance.militar = militar
                instance.save()

            outros_memorial_instances = outros_memorial_formset.save(commit=False)
            for instance in outros_memorial_instances:
                instance.memorial = memorial_instances[0]  # associando ao primeiro memorial salvo
                instance.save()

            return redirect('militares:lista_memoriais')
    else:
        memorial_formset = MemorialFormSet(queryset=MemorialDeCalculo.objects.none(), initial=[{'RE_do_MilitarIncluso': militar.RE}], prefix='memorial')
        outros_memorial_formset = OutrosMemorialFormSet(queryset=OutrosMemorial.objects.none(), prefix='outros')

    context = {
        'militar': militar,
        'memorial_formset': memorial_formset,
        'outros_memorial_formset': outros_memorial_formset
    }
    return render(request, 'criar_memorial.html', context)



class CriarMemorialView(CreateView):
    model = MemorialDeCalculo
    template_name = 'criar_memorial.html'
    form_class = MemorialDeCalculoForm

    def get_initial(self):
        initial = super().get_initial()
        RE_do_MilitarIncluso = self.request.GET.get('RE_do_MilitarIncluso')
        if RE_do_MilitarIncluso:
            try:
                militar = MilitarIncluso.objects.get(RE=RE_do_MilitarIncluso)
                tb_vencimento = TB_Vencimentos.objects.filter(Posto_Grad=militar.posto_graduacao).first()
                if tb_vencimento:
                    initial['salario_padrao'] = tb_vencimento.Salario_Padrao
            except MilitarIncluso.DoesNotExist:
                pass
        return initial

class CriarMemorialView(View):
    def get(self, request, *args, **kwargs):
        MemorialFormSet = modelformset_factory(MemorialDeCalculo, form=MemorialDeCalculoForm, extra=1)
        OutrosMemorialFormSet = modelformset_factory(OutrosMemorial, form=OutrosMemorialForm, extra=1)

        memorial_form = MemorialDeCalculoForm()
        outros_memorial_formset = OutrosMemorialFormSet(queryset=OutrosMemorial.objects.none())

        return render(request, 'criar_memorial.html', {
            'memorial_form': memorial_form,
            'outros_memorial_formset': outros_memorial_formset
        })

    def post(self, request, *args, **kwargs):
        MemorialFormSet = modelformset_factory(MemorialDeCalculo, form=MemorialDeCalculoForm, extra=1)
        OutrosMemorialFormSet = modelformset_factory(OutrosMemorial, form=OutrosMemorialForm, extra=1)

        memorial_form = MemorialDeCalculoForm(request.POST)
        outros_memorial_formset = OutrosMemorialFormSet(request.POST)

        if memorial_form.is_valid() and outros_memorial_formset.is_valid():
            memorial_instance = memorial_form.save()
            outros_memorial_instances = outros_memorial_formset.save(commit=False)
            for instance in outros_memorial_instances:
                instance.memorial = memorial_instance
                instance.save()
            return redirect('militares:lista_memoriais')

        return render(request, 'criar_memorial.html', {
            'memorial_form': memorial_form,
            'outros_memorial_formset': outros_memorial_formset
        })


def militares_finalizados(request):
    militares = FinalizadoMilitar.objects.all()
    return render(request, 'militares_finalizados.html', {'militares': militares})

def militar_finalizado_detail(request, re):
    militar = get_object_or_404(FinalizadoMilitar, RE=re)
    beneficiarios = FinalizadoBeneficiario.objects.filter(militar=militar)
    return render(request, 'militar_finalizado_detail.html', {'militar': militar, 'beneficiarios': beneficiarios})
