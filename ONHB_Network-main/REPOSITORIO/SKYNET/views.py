from django.shortcuts import get_object_or_404, render
from .models import EDICAO, FASE, QUESTAO, ITEM, TAG, PERIODO, DOCUMENTO, ANO_HISTORICO,TIPO_QUESTAO


def escolher_edicao(request):
    
    edicoes = EDICAO.objects.all().order_by('-ano_edicao')
    
   
    return render(request, 'SKYNET/escolher_edicao.html', {'edicoes': edicoes})

def escolher_fase(request, edicao_id):
    
    edicao = get_object_or_404(EDICAO, id_edicao=edicao_id)
    
    
    fases = FASE.objects.filter(id_edicao=edicao).order_by('num_fase')
    
    
    return render(request, 'SKYNET/escolher_fase.html', {
        'edicao': edicao, 
        'fases': fases
    })

def listar_questoes(request, fase_id):

    
    fase = get_object_or_404(FASE, id_fase=fase_id)
    
     
    questoes = QUESTAO.objects.filter(id_fase=fase).order_by('num_questao')

    busca_tipo = request.GET.get('tipos')
    busca_periodo = request.GET.get('periodos')
    busca_documento = request.GET.get('documento')
    busca_tag = request.GET.get('tags')
    busca_ano = request.GET.get('anos')
            
    
    if busca_documento:
        
        questoes = questoes.filter(documentos__nome_documento__icontains=busca_documento)
            
    if busca_tipo:
        
        questoes = questoes.filter(id_tipo_questao__tipo_nome__iexact=busca_tipo)
            
    if busca_periodo:
        
        questoes = questoes.filter(periodos__periodo_nome__iexact=busca_periodo)

    if busca_tag:
        questoes = questoes.filter(tags__tag_nome__icontains=busca_tag)

    if busca_ano:
        questoes = questoes.filter(anos__ano__icontains=busca_ano)

    questoes = questoes.distinct()
            
   
    return render(request, 'SKYNET/listar_questoes.html', {
        'fase': fase,
        'questoes': questoes
    })

def detalhes_questao(request, questao_id):
            
    
    questao = get_object_or_404(QUESTAO, id_questao=questao_id)
    
    
    alternativas = ITEM.objects.filter(id_questao=questao).order_by('identificador')
    
    
    
    return render(request, 'SKYNET/detalhes_questao.html', {
        'questao': questao,
        'alternativas': alternativas
    })

def busca_global(request):
    # Começa pegando todas as questões do banco
    questoes = QUESTAO.objects.all().select_related('id_fase', 'id_fase__id_edicao', 'id_tipo_questao')

    # Captura os parâmetros GET do formulário
    busca_documento = request.GET.get('documento', '')
    busca_tipo = request.GET.get('tipos', '')
    busca_ano = request.GET.get('anos', '')
    busca_tag = request.GET.get('tags', '')
    busca_periodo = request.GET.get('periodos', '')
    busca_enunciado = request.GET.get('enunciado', '')

    # Aplica os filtros dinamicamente
    if busca_documento:
        questoes = questoes.filter(documentos__nome_documento__icontains=busca_documento)
    if busca_tipo:
        questoes = questoes.filter(id_tipo_questao__tipo_nome__icontains=busca_tipo)
    if busca_ano:
        questoes = questoes.filter(anos__ano__icontains=busca_ano)
    if busca_tag:
        questoes = questoes.filter(tags__tag_nome__icontains=busca_tag)
    if busca_periodo:
        questoes = questoes.filter(periodos__periodo_nome__icontains=busca_periodo)
    if busca_enunciado:
        questoes = questoes.filter(enunciado__icontains=busca_enunciado)

    # Evita resultados duplicados caso uma questão tenha múltiplas tags/docs correspondentes
    questoes = questoes.distinct()

    context = {
        'questoes': questoes,
        'busca_documento': busca_documento,
        'busca_tipo': busca_tipo,
        'busca_ano': busca_ano,
        'busca_tag': busca_tag,
        'busca_periodo': busca_periodo,
        'busca_enunciado': busca_enunciado,
    }
    return render(request, 'SKYNET/busca_global.html', context)