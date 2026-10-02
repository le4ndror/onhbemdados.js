from django.contrib import admin
from .models import QUESTAO, ITEM, EDICAO, TIPO_QUESTAO, FASE, PERIODO, DOCUMENTO, ANO_HISTORICO, TAG

class ITEMInline(admin.TabularInline):
    """Permite visualizar e editar as alternativas direto dentro da página da Questão!"""
    model = ITEM
    extra = 4 

@admin.register(EDICAO)
class EdicaoAdmin(admin.ModelAdmin):
    list_display = ('id_edicao', 'num_edicao', 'ano_edicao')
    list_filter = ('ano_edicao',)
    search_fields = ('num_edicao',)

@admin.register(FASE)
class FaseAdmin(admin.ModelAdmin):
    list_display = ('id_fase', 'num_fase', 'id_edicao', 'tipo_fase')
    list_filter = ('tipo_fase', 'id_edicao')


admin.site.register(TIPO_QUESTAO)

@admin.register(QUESTAO)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ('id_questao', 'num_questao', 'id_fase', 'id_tipo_questao', 'resumo_enunciado')
    list_filter = ('id_fase__id_edicao', 'id_fase', 'id_tipo_questao',)
    search_fields = ('enunciado',)

    
    inlines = [ITEMInline]

    def resumo_enunciado(self, obj):
        """Cria um resumo do enunciado para não quebrar o layout da tabela"""
        return obj.enunciado[:80] + '...' if len(obj.enunciado) > 80 else obj.enunciado
    resumo_enunciado.short_description = 'Enunciado (Trecho)'

@admin.register(ITEM)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id_item', 'identificador', 'pontuacao', 'id_questao')
    list_filter = ('pontuacao', 'identificador',) 
    search_fields = ('texto',)
    
@admin.register(PERIODO)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id_periodo', 'periodo_nome', 'seculo')
    list_filter = ('periodo_nome','seculo',)
    search_fields = ('periodo_nome', 'seculo')

@admin.register(DOCUMENTO)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id_documento', 'nome_documento', 'tipo_documento')
    list_filter = ('tipo_documento',)
    search_fields = ( 'nome_documento', 'tipo_documento')

@admin.register(ANO_HISTORICO)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id_ano', 'ano')
    
    search_fields = ('ano',)

@admin.register(TAG)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id_tag', 'tag_nome')
    
    search_fields = ('tag_nome',)