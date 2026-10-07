import csv
from django.core.management.base import BaseCommand
from SKYNET.models import EDICAO, FASE, TIPO_QUESTAO, QUESTAO, ITEM, DOCUMENTO, PERIODO, ANO_HISTORICO, TAG

class Command(BaseCommand):
    help = 'Esteira automatizada para importar os 5 arquivos CSV tratando as imperfeições de texto.'

    def handle(self, *args, **options):
        
        # -------------------------------------------------------------------------
        # PASSO 1: IMPORTAR EDIÇÕES
        # -------------------------------------------------------------------------
        csv_edicao = 'DADOS_EDICAO.csv'
        self.stdout.write(self.style.WARNING(f"\n➔ Passo 1/5: Importando Edições..."))
        try:
            with open(csv_edicao, mode='r', encoding='utf-8-sig') as f:
                leitor = csv.DictReader(f, delimiter=';')
                criadas, atualizadas = 0, 0
                for linha in leitor:
                    if not linha.get('id_edicao'): continue
                    
                    obj, criado = EDICAO.objects.update_or_create(
                        id_edicao=int(linha['id_edicao']),
                        defaults={
                            'num_edicao': int(linha['num_edicao']),
                            'ano_edicao': int(linha['ano_edicao'])
                        }
                    )
                    if criado: criadas += 1
                    else: atualizadas += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Edições -> Criadas: {criadas} | Atualizadas: {atualizadas}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_edicao}"))

        # -------------------------------------------------------------------------
        # PASSO 2: IMPORTAR TIPOS DE QUESTÃO
        # -------------------------------------------------------------------------
        csv_tipo = 'DADOS_TIPO_QUESTAO.csv'
        self.stdout.write(self.style.WARNING(f"\n➔ Passo 2/5: Importando Tipos de Questão..."))
        try:
            with open(csv_tipo, mode='r', encoding='latin-1') as f:
                leitor = csv.DictReader(f, delimiter=';')
                criadas, atualizadas = 0, 0
                for linha in leitor:
                    if not linha.get('id_tipo_questao'): continue
                    
                    obj, criado = TIPO_QUESTAO.objects.update_or_create(
                        id_tipo_questao=int(linha['id_tipo_questao']),
                        defaults={'tipo_nome': linha['tipo_nome'].strip()}
                    )
                    if criado: criadas += 1
                    else: atualizadas += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Tipos -> Criados: {criadas} | Atualizados: {atualizadas}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_tipo}"))

        # -------------------------------------------------------------------------
        # PASSO 3: IMPORTAR FASES
        # -------------------------------------------------------------------------
        csv_fase = 'DADOS_FASE.csv'
        self.stdout.write(self.style.WARNING(f"\n➔ Passo 3/5: Importando Fases..."))
        try:
            with open(csv_fase, mode='r', encoding='utf-8-sig') as f:
                leitor = csv.DictReader(f, delimiter=';')
                criadas, atualizadas = 0, 0
                for linha in leitor:
                    if not linha.get('id_fase'): continue
                    
                    edicao_obj = EDICAO.objects.get(id_edicao=int(linha['id_edicao']))
                    
                    obj, criado = FASE.objects.update_or_create(
                        id_fase=int(linha['id_fase']),
                        defaults={
                            'num_fase': int(linha['num_fase']),
                            'tipo_fase': linha['tipo_fase'].strip(),
                            'id_edicao': edicao_obj
                        }
                    )
                    if criado: criadas += 1
                    else: atualizadas += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Fases -> Criadas: {criadas} | Atualizadas: {atualizadas}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_fase}"))

        # -------------------------------------------------------------------------
        # PASSO 4: IMPORTAR QUESTÕES (Com Limpeza de Caracteres)
        # -------------------------------------------------------------------------
        csv_questao = 'DADOS_QUESTAO.csv'
        self.stdout.write(self.style.WARNING(f"\n➔ Passo 4/5: Importando Questões..."))
        try:
            with open(csv_questao, mode='r', encoding='utf-8-sig') as f:
                leitor = csv.DictReader(f, delimiter=';')
                criadas, atualizadas = 0, 0
                for linha in leitor:
                    if not linha.get('id_questao'): continue
                    
                    fase_obj = FASE.objects.get(id_fase=int(linha['id_fase']))
                    tipo_obj = TIPO_QUESTAO.objects.get(id_tipo_questao=int(linha['id_tipo_questao']))
                    
                    enunciado_bruto = linha['enunciado']
                    enunciado_limpo = enunciado_bruto.strip()
                    
                    while enunciado_limpo.startswith('"') and enunciado_limpo.endswith('"'):
                        enunciado_limpo = enunciado_limpo[1:-1].strip()
                    
                    enunciado_limpo = enunciado_limpo.replace('\n', ' ').replace('\r', '')

                    obj, criado = QUESTAO.objects.update_or_create(
                        id_questao=int(linha['id_questao']),
                        defaults={
                            'num_questao': int(linha['num_questao']),
                            'enunciado': enunciado_limpo,
                            'id_fase': fase_obj,
                            'id_tipo_questao': tipo_obj
                        }
                    )
                    
                    if criado: 
                        criadas += 1
                    else: 
                        atualizadas += 1
                        
                self.stdout.write(self.style.SUCCESS(f"✔ Questões -> Criadas: {criadas} | Atualizadas: {atualizadas}\n"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_questao}"))


        # 🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩 ADICIONADO DAQUI EM DIANTE 🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩
        # -------------------------------------------------------------------------
        # PASSO 5: IMPORTAR ITENS / ALTERNATIVAS (Tratando aspas e quebras)
        # -------------------------------------------------------------------------
        csv_item = 'DADOS_ITEM.csv'
        self.stdout.write(self.style.WARNING(f"➔ Passo 5/5: Importando Itens/Alternativas..."))
        try:
            with open(csv_item, mode='r', encoding='utf-8-sig') as f:
                leitor = csv.DictReader(f, delimiter=';')
                criados, atualizados = 0, 0
                for linha in leitor:
                    # Proteção contra linhas vazias no fim do CSV
                    if not linha.get('id_item'): continue
                    
                    # Relaciona o ITEM com a sua respectiva QUESTAO (Chave Estrangeira)
                    questao_obj = QUESTAO.objects.get(id_questao=int(linha['id_questao']))
                    
                    # Higienização do texto da alternativa (remove aspas e quebras de linha)
                    texto_bruto = linha['texto'].strip()
                    while texto_bruto.startswith('"') and texto_bruto.endswith('"'):
                        texto_bruto = texto_bruto[1:-1].strip()
                    texto_limpo = texto_bruto.replace('\n', ' ').replace('\r', '')

                    # 🚩 ALTERAÇÃO AQUI: Tratamento para evitar o erro de pontuação vazia
                    try:
                        pontuacao_final = int(linha['pontuacao'])
                    except (ValueError, TypeError):
                        # Se estiver vazio ou não for um número válido, define como 0 por padrão
                        pontuacao_final = 0

                    # Cria ou atualiza no banco de dados de forma segura
                    obj, criado = ITEM.objects.update_or_create(
                        id_item=int(linha['id_item']),
                        defaults={
                            'identificador': linha['identificador'].strip(), # Ex: A, B, C, D
                            'texto': texto_limpo,
                            'pontuacao': pontuacao_final, # Usa a pontuação tratada aqui!
                            'id_questao': questao_obj
                        }
                    )
                    if criado: criados += 1
                    else: atualizados += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Itens -> Criados: {criados} | Atualizados: {atualizados}\n"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_item}"))
        # 🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩 FINAL DO BLOCO ADICIONADO 🚩🚩🚩🚩🚩🚩🚩🚩🚩🚩

        # -------------------------------------------------------------------------
        # PASSO 6/9: IMPORTAR DOCUMENTOS (Tratando aspas internas)
        # -------------------------------------------------------------------------
        csv_documento = 'DADOS_DOCUMENTO.csv'  # Confirme se o seu arquivo tem exatamente este nome
        self.stdout.write(self.style.WARNING(f"➔ Passo 6/9: Importando Documentos Históricos..."))
        try:
            with open(csv_documento, mode='r', encoding='utf-8-sig') as f:
                leitor = csv.DictReader(f, delimiter=';')
                criados, atualizados = 0, 0
                for linha in leitor:
                    if not linha.get('id_documento'): continue
                    
                    # Limpeza das aspas externas e tratamento de aspas duplas no meio do texto (Ex: ""Triste Fim"")
                    nome_bruto = linha['nome_documento'].strip()
                    while nome_bruto.startswith('"') and nome_bruto.endswith('"'):
                        nome_bruto = nome_bruto[1:-1].strip()
                    # Substitui as duas aspas juntas por apenas uma aspa normal
                    nome_limpo = nome_bruto.replace('""', '"')

                    tipo_limpo = linha['tipo_documento'].strip()

                    # Cria ou atualiza no banco de dados
                    obj, criado = DOCUMENTO.objects.update_or_create(
                        id_documento=int(linha['id_documento']),
                        defaults={
                            'nome_documento': nome_limpo,
                            'tipo_documento': tipo_limpo
                        }
                    )
                    if criado: criados += 1
                    else: atualizados += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Documentos -> Criados: {criados} | Atualizados: {atualizados}\n"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_documento}"))

        # -------------------------------------------------------------------------
        # PASSO 7/9: IMPORTAR ANOS HISTÓRICOS
        # -------------------------------------------------------------------------
        csv_ano_historico = 'DADOS_ANO_HISTORICO.csv' # Confirme o nome do seu arquivo CSV
        self.stdout.write(self.style.WARNING(f"➔ Passo 7/9: Importando Anos Históricos..."))
        try:
            with open(csv_ano_historico, mode='r', encoding='utf-8-sig') as f:
                leitor = csv.DictReader(f, delimiter=';')
                criados, atualizados = 0, 0
                for linha in leitor:
                    if not linha.get('id_ano'): continue

                    # Cria ou atualiza no banco de dados convertendo os dois campos para inteiros
                    obj, criado = ANO_HISTORICO.objects.update_or_create(
                        id_ano=int(linha['id_ano']),
                        defaults={
                            'ano': int(linha['ano'])
                        }
                    )
                    if criado: criados += 1
                    else: atualizados += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Anos Históricos -> Criados: {criados} | Atualizados: {atualizados}\n"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_ano_historico}"))

        # -------------------------------------------------------------------------
        # PASSO 8/9: IMPORTAR TAGS (Tratando acentuação e caracteres estranhos)
        # -------------------------------------------------------------------------
        csv_tag = 'DADOS_TAG.csv' # Confirme o nome do seu arquivo CSV
        self.stdout.write(self.style.WARNING(f"➔ Passo 8/9: Importando Tags Temáticas..."))
        try:
            # 💡 Mudamos para encoding='latin-1' para resolver os caracteres quebrados ()
            with open(csv_tag, mode='r', encoding='latin-1') as f:
                leitor = csv.DictReader(f, delimiter=';')
                criados, atualizados = 0, 0
                for linha in leitor:
                    if not linha.get('id_tag'): continue

                    # Limpa espaços em branco bobos nas pontas do nome da tag
                    nome_tag_limpo = linha['tag_nome'].strip()

                    # Cria ou atualiza no banco de dados de forma segura
                    obj, criado = TAG.objects.update_or_create(
                        id_tag=int(linha['id_tag']),
                        defaults={
                            'tag_nome': nome_tag_limpo
                        }
                    )
                    if criado: criados += 1
                    else: atualizados += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Tags -> Criadas: {criados} | Atualizados: {atualizados}\n"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_tag}"))

        # -------------------------------------------------------------------------
        # PASSO 9/9: IMPORTAR PERÍODOS HISTÓRICOS
        # -------------------------------------------------------------------------
        csv_periodo = 'DADOS_PERIODO.csv' # Confirme o nome do seu arquivo CSV
        self.stdout.write(self.style.WARNING(f"➔ Passo 9/9: Importando Períodos Históricos..."))
        try:
            with open(csv_periodo, mode='r', encoding='latin-1') as f:
                leitor = csv.DictReader(f, delimiter=';')
                criados, atualizados = 0, 0
                for linha in leitor:
                    if not linha.get('id_periodo'): continue

                    # Cria ou atualiza no banco de dados
                    obj, criado = PERIODO.objects.update_or_create(
                        id_periodo=int(linha['id_periodo']),
                        defaults={
                            'periodo_nome': linha['periodo_nome'].strip(),
                            'seculo': int(linha['seculo']) # Converte o número do século para inteiro
                        }
                    )
                    if criado: criados += 1
                    else: atualizados += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Períodos -> Criados: {criados} | Atualizados: {atualizados}\n"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_periodo}"))

        # -------------------------------------------------------------------------
        # PASSO 10: ASSOCIAR QUESTÕES E DOCUMENTOS (PROTÓTIPO)
        # -------------------------------------------------------------------------
        csv_assoc_doc = 'DADOS_QD.csv' # Confirme se o nome está exatamente igual
        self.stdout.write(self.style.WARNING(f"➔ Passo 10: Vinculando Documentos às Questões..."))
        try:
            with open(csv_assoc_doc, mode='r', encoding='utf-8-sig') as f:
                leitor = csv.DictReader(f, delimiter=';')
                vinculos_criados = 0
                for linha in leitor:
                    # Garante que temos os dois IDs na linha do CSV
                    if not linha.get('id_questao') or not linha.get('id_documento'): 
                        continue
                    
                    try:
                        # 1. Busca a questão correspondente no banco
                        questao_obj = QUESTAO.objects.get(id_questao=int(linha['id_questao']))
                        # 2. Busca o documento correspondente no banco
                        documento_obj = DOCUMENTO.objects.get(id_documento=int(linha['id_documento']))
                        
                        # 3. Faz a associação na tabela intermediária automática do Django
                        questao_obj.documentos.add(documento_obj)
                        vinculos_criados += 1
                        
                    except QUESTAO.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"⚠ Questão ID {linha['id_questao']} não encontrada no banco."))
                    except DOCUMENTO.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"⚠ Documento ID {linha['id_documento']} não encontrado no banco."))
                        
                self.stdout.write(self.style.SUCCESS(f"✔ Relações criadas com sucesso: {vinculos_criados}\n"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_assoc_doc}"))

        # -------------------------------------------------------------------------
        # PASSO 11: ASSOCIAR QUESTÕES E PERÍODOS
        # -------------------------------------------------------------------------
        csv_assoc_doc = 'DADOS_QP.csv'
        self.stdout.write(self.style.WARNING(f"➔ Passo 11: Vinculando Períodos às Questões..."))
        try:
            with open(csv_assoc_doc, mode='r', encoding='utf-8-sig') as f:
                leitor = csv.DictReader(f, delimiter=';')
                vinculos_criados = 0
                for linha in leitor:
                    if not linha.get('id_questao') or not linha.get('id_periodo'): 
                        continue
                    
                    try:
                        questao_obj = QUESTAO.objects.get(id_questao=int(linha['id_questao']))
                        periodo_obj = PERIODO.objects.get(id_periodo=int(linha['id_periodo']))
                        
                        questao_obj.periodos.add(periodo_obj)
                        vinculos_criados += 1
                        
                    except QUESTAO.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"⚠ Questão ID {linha['id_questao']} não encontrada."))
                    except PERIODO.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"⚠ Período ID {linha['id_periodo']} não encontrado."))
                        
                # AVISO FORA DO LOOP FOR (Executa 1 vez no final)
                self.stdout.write(self.style.SUCCESS(f"✔ Períodos vinculados com sucesso: {vinculos_criados}\n"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_assoc_doc}"))

        # -------------------------------------------------------------------------
        # PASSO 12: ASSOCIAR QUESTÕES E TAGS
        # -------------------------------------------------------------------------
        csv_assoc_doc = 'DADOS_QT.csv'
        self.stdout.write(self.style.WARNING(f"➔ Passo 12: Vinculando Tags às Questões..."))
        try:
            with open(csv_assoc_doc, mode='r', encoding='latin-1') as f:
                leitor = csv.DictReader(f, delimiter=';')
                vinculos_criados = 0
                for linha in leitor:
                    if not linha.get('id_questao') or not linha.get('id_tag'): 
                        continue
                    
                    try:
                        questao_obj = QUESTAO.objects.get(id_questao=int(linha['id_questao']))
                        tag_obj = TAG.objects.get(id_tag=int(linha['id_tag']))
                        
                        questao_obj.tags.add(tag_obj)
                        vinculos_criados += 1
                        
                    except QUESTAO.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"⚠ Questão ID {linha['id_questao']} não encontrada."))
                    except TAG.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"⚠ TAG ID {linha['id_tag']} não encontrada."))
                        
                self.stdout.write(self.style.SUCCESS(f"✔ Tags vinculadas com sucesso: {vinculos_criados}\n"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_assoc_doc}"))

        # -------------------------------------------------------------------------
        # PASSO 13: ASSOCIAR QUESTÕES E ANOS HISTÓRICOS
        # -------------------------------------------------------------------------
        csv_assoc_doc = 'DADOS_QA.csv'
        self.stdout.write(self.style.WARNING(f"➔ Passo 13: Vinculando Anos Históricos às Questões..."))
        try:
            with open(csv_assoc_doc, mode='r', encoding='utf-8-sig') as f:
                leitor = csv.DictReader(f, delimiter=';')
                vinculos_criados = 0
                for linha in leitor:
                    if not linha.get('id_questao') or not linha.get('id_ano'): 
                        continue
                    
                    try:
                        questao_obj = QUESTAO.objects.get(id_questao=int(linha['id_questao']))
                        ano_obj = ANO_HISTORICO.objects.get(id_ano=int(linha['id_ano']))
                        
                        # ATENÇÃO: Confirme se o campo no models.py chama 'anos' ou 'anos_historicos'
                        questao_obj.anos.add(ano_obj) 
                        vinculos_criados += 1
                        
                    except QUESTAO.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"⚠ Questão ID {linha['id_questao']} não encontrada."))
                    except ANO_HISTORICO.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"⚠ Ano Histórico ID {linha['id_ano']} não encontrado."))
                        
                self.stdout.write(self.style.SUCCESS(f"✔ Anos Históricos vinculados com sucesso: {vinculos_criados}\n"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"✘ Arquivo não encontrado: {csv_assoc_doc}"))