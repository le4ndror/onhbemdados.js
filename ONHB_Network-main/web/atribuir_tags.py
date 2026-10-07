#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atribui tags existentes as questoes, somente quando o conteudo combina."""

import csv
import os
import re
import sqlite3
import unicodedata

RAIZ = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "REPOSITORIO"))
DB = os.path.join(RAIZ, "db.sqlite3")
CSV_QT = os.path.join(RAIZ, "DADOS_QT.csv")


def sem_acento(texto):
    texto = unicodedata.normalize("NFD", texto or "")
    return "".join(c for c in texto if unicodedata.category(c) != "Mn").lower()


def tem_frase(texto, frase):
    return sem_acento(frase) in texto


def tem_palavra(texto, palavra):
    p = re.escape(sem_acento(palavra))
    return re.search(r"(?<![a-z0-9])" + p + r"(?![a-z0-9])", texto) is not None


def qualquer(texto, termos):
    for t in termos:
        if " " in t:
            if tem_frase(texto, t):
                return True
        elif tem_palavra(texto, t):
            return True
    return False


# Regras: tag_id -> termos que PRECISAM aparecer no conteudo.
# Ordem: do mais especifico para o mais generico.
REGRAS = [
    (125, ["inteligencia artificial", "inteligencia artificial", "chatgpt", "ia generativa"]),
    (124, ["fake news", "desinformacao", "noticia falsa", "noticias falsas"]),
    (64, ["fernando collor", "collor", "impeachment"]),
    (66, ["getulio vargas", "getúlio vargas", "era vargas", "estado novo", "vargas"]),
    (65, ["machado de assis"]),
    (17, ["lima barreto"]),
    (23, ["lampiao", "lampião"]),
    (71, ["tiradentes", "inconfidencia mineira", "inconfidência mineira"]),
    (68, ["conjuracao bahiana", "conjuracao baiana", "conjuração bahiana", "conjuração baiana"]),
    (5, ["carta de caminha", "pero vaz de caminha", "caminha"]),
    (81, ["palmares", "zumbi"]),
    (43, ["integralismo", "integralista", "plínio salgado", "plinio salgado"]),
    (34, ["revolta da chibata", "chibata", "joao candido", "joão cândido"]),
    (29, ["guerra do paraguai", "guerra do paraguay", "paraguai"]),
    (24, ["cangaco", "cangaço", "cangaceiro"]),
    (102, ["plano de metas", "50 anos em 5"]),
    (111, ["carta testamento", "carta-testamento"]),
    (30, ["holandeses no brasil", "holandeses", "nassau", "pernambuco holandes", "invasao holandesa"]),
    (89, ["segunda guerra mundial", "ii guerra mundial", "2a guerra", "segunda guerra", "nazismo", "hitler"]),
    (46, ["segunda guerra mundial", "ii guerra mundial", "2a guerra", "segunda guerra"]),
    (74, ["ditadura militar", "regime militar", "ai-5", "ai5", "golpe de 1964", "golpe militar", "anos de chumbo"]),
    (44, ["ditadura", "autoritarismo", "censura", "repressao militar"]),
    (107, ["anistia"]),
    (45, ["tortura", "torturado", "doi-codi", "doi codi"]),
    (76, ["comunismo", "comunista", "pcb", "marxismo"]),
    (94, ["republica velha", "república velha", "oligarquia"]),
    (95, ["coronelismo", "coronéis", "coroneis"]),
    (100, ["desenvolvimentismo", "desenvolvimentista", "jk", "juscelino"]),
    (80, ["constituicao federal", "constituição federal", "constituicao de 1988", "constituicao cidadã"]),
    (118, ["constituicao", "constituição", "constituinte"]),
    (70, ["abolicao", "abolição", "lei aurea", "lei áurea", "13 de maio"]),
    (92, ["abolicionismo", "abolicionista"]),
    (21, ["escravidao", "escravidão", "escravo", "escravos", "escravizado", "tráfico negreiro", "trafico negreiro"]),
    (113, ["quilombo", "quilombos", "quilombola"]),
    (39, ["trabalho indigena", "indios escrav", "indígena escrav", "aldeamento"]),
    (121, ["povos indigenas", "indigena", "indígena", "indios", "índios", "tupinamba", "tupinambá", "guarani", "nambiquara"]),
    (40, ["populacao nativa", "nativos", "nativo da costa", "povos originarios"]),
    (51, ["jesuita", "jesuíta", "jesuitas", "companhia de jesus", "anchieta", "nóbrega", "nobrega"]),
    (52, ["bandeirante", "bandeirantes"]),
    (49, ["conselho ultramarino"]),
    (77, ["engenho", "engenhos", "cana-de-acucar", "cana de acucar", "açúcar", "acucar"]),
    (13, ["mineracao", "mineração", "ouro", "minas gerais", "garimpo"]),
    (7, ["colonizacao", "colonização", "colonia", "colônia", "colonial", "colonos"]),
    (8, ["formacao do territorio", "territorio nacional", "fronteira", "limites territoriais"]),
    (86, ["expansao do territorio", "expansão territorial", "tratado de tordesilhas", "tordesilhas", "tratado de madri"]),
    (15, ["mapas brasil", "mapa do brasil", "mapa do brasil"]),
    (63, ["cartografia", "cartografico", "mapa", "mapas"]),
    (69, ["amazonia", "amazônia", "amazonico", "floresta amazonica"]),
    (79, ["povoamento da america", "povoamento da américa", "ocupacao da america", "chegada do homem"]),
    (57, ["pre-historia", "pré-história", "pre historia", "paleolitico", "sambaqui"]),
    (98, ["era glacial", "glacial", "glaciacao"]),
    (99, ["clima tropical", "tropical"]),
    (56, ["arqueologia", "arqueologico", "sítio arqueologico", "sitio arqueologico"]),
    (122, ["arqueologia historica"]),
    (41, ["imigracao", "imigração", "imigrante", "imigrantes", "colonos alemaes", "italianos"]),
    (32, ["industria automobilistica", "indústria automobilística", "ford", "volkswagen", "automobilist"]),
    (31, ["automovel", "automóvel", "carro", "automoveis"]),
    (101, ["rodovia", "rodovias", "estrada de rodagem"]),
    (104, ["industrializacao", "industrialização", "industria", "fábrica", "fabrica"]),
    (36, ["classe operaria", "classe operária", "operario", "operários", "operariado"]),
    (103, ["operarias", "operárias", "operaria"]),
    (14, ["atividades economicas", "economia", "comercio", "comércio", "exportacao", "agroexportadora"]),
    (47, ["navegacao a vapor", "navegação a vapor", "vapor", "navio a vapor"]),
    (10, ["urbanizacao", "urbanização", "reforma urbana", "cidade moderna"]),
    (19, ["cidade", "cidades", "metropole", "metrópole"]),
    (97, ["espaco urbano", "espaço urbano", "rua", "logradouro"]),
    (96, ["cortico", "cortiço", "corticos"]),
    (60, ["pobreza urbana", "pobreza", "miseria", "favela"]),
    (61, ["desigualdade social", "desigualdade", "exclusao social"]),
    (12, ["cultura material", "objeto", "artefato", "utensilio"]),
    (18, ["literatura", "romance", "poema", "poesia", "literario"]),
    (35, ["texto literario", "texto literário", "trecho do romance", "cronica"]),
    (22, ["imprensa", "jornal", "gazeta", "periodico", "periódico", "reportagem"]),
    (119, ["imprensa feminina", "jornal feminino", "revista feminina"]),
    (72, ["propaganda", "anuncio", "anúncio", "publicidade", "cartaz"]),
    (83, ["iconografia", "gravura", "pintura", "fotografia", "charge"]),
    (75, ["musica", "música", "canção", "cancao", "samba", "canto"]),
    (115, ["cinema", "filme", "cinematograf"]),
    (116, ["arte urbana", "street art"]),
    (117, ["grafite", "graffiti", "pichacao"]),
    (62, ["futebol", "jogador de futebol", "copa do mundo"]),
    (67, ["museu", "museus", "acervo museologico"]),
    (78, ["patrimonio cultural", "patrimônio", "patrimonio historico", "tombamento"]),
    (106, ["barroco", "aleijadinho"]),
    (109, ["arquitetura religiosa", "igreja", "capela", "catedral"]),
    (91, ["festa", "festas", "procissao", "procissão", "carnaval"]),
    (90, ["religiao", "religião", "religioso", "igreja", "catolic", "protestant"]),
    (85, ["messianismo", "messianico", "canudos", "conselheiro", "sebastianismo"]),
    (110, ["hospicio", "hospício", "manicomio", "loucura"]),
    (105, ["saude publica", "saúde pública", "epidemia", "vacina", "higiene", "saneamento"]),
    (82, ["epidemia", "epidemias", "peste", "gripe", "varíola", "variola", "covid"]),
    (87, ["ciencia", "ciência", "cientifico", "científico"]),
    (58, ["historia da ciencia", "história da ciência", "cientista"]),
    (112, ["educacao", "educação", "escola", "ensino", "aluno", "professor"]),
    (38, ["mulher", "mulheres", "feminina"]),
    (88, ["historia da mulher", "história da mulher", "condicao feminina"]),
    (120, ["feminismo", "feminista", "sufragio feminino"]),
    (37, ["voto", "eleicao", "eleição", "eleitoral", "urna"]),
    (108, ["direitos politicos", "direitos políticos", "cidadania", "direito de votar"]),
    (84, ["leis e direitos", "codigo penal", "código penal", "direitos civis"]),
    (50, ["representacao politica", "representação política", "parlamento", "camara", "assembleia"]),
    (42, ["cultura politica", "cultura política", "ideologia", "nacionalismo"]),
    (54, ["nacao", "nação", "patria", "pátria", "identidade nacional"]),
    (59, ["identidade nacional", "identidade brasileira", "brasilidade"]),
    (55, ["monarquia", "imperio", "império", "d. pedro", "dom pedro", "imperador"]),
    (25, ["movimentos sociais", "movimento social", "protesto", "revolta", "greve", "luta popular"]),
    (33, ["punicao", "punição", "castigo", "chibatada", "suplicio"]),
    (114, ["exilio", "exílio", "exilado", "desterro"]),
    (73, ["historia oral", "história oral", "depoimento", "entrevista", "memoria oral"]),
    (53, ["historiografia", "historiador", "escrita da historia", "interpretacao historica"]),
    (93, ["producao textual", "produção textual", "produzir um documento", "redija", "escreva um"]),
    (48, ["carta", "cartas", "epistolar", "missiva"]),
    (26, ["viajante", "viajantes", "relato de viagem", "cronista"]),
    (27, ["usos e costumes", "costumes", "habito", "hábitos", "tradição", "tradicao"]),
    (28, ["vida cotidiana", "cotidiano", "dia a dia", "quotidiano"]),
    (123, ["consumo", "consumidor", "mercadoria", "publicidade de produtos"]),
    (1, ["computador", "computadores", "microcomputador", "tk95", "tk 95", "tk85"]),
    (2, ["comunicacoes", "comunicações", "telefone", "radio", "rádio"]),
    (3, ["tecnologia", "tecnologico"]),
    (16, ["seculo xxi", "século xxi", "sec. xxi", "séc. xxi", "anos 2000", "século 21"]),
    (9, ["seculo xx", "século xx", "sec. xx", "séc. xx", "século 20", "séc xx"]),
    (4, ["seculo xx", "século xx", "séc xx", "sec xx"]),
    (20, ["seculo xix", "século xix", "séc. xix", "século 19"]),
    (11, ["seculo xviii", "século xviii", "séc. xviii", "século 18"]),
    (6, ["seculo xvi", "século xvi", "séc. xvi", "século 16"]),
]


def inferir_tags(texto, docs_texto):
    blob = sem_acento(texto + " " + docs_texto)
    ids = []
    vistos = set()
    for tag_id, termos in REGRAS:
        if tag_id in vistos:
            continue
        if qualquer(blob, termos):
            ids.append(tag_id)
            vistos.add(tag_id)
        if len(ids) >= 4:
            break
    return ids


def fallback(texto, docs_tipos, docs_nomes):
    blob = sem_acento(texto + " " + docs_nomes)
    tipos = sem_acento(docs_tipos)
    candidatos = []
    pares = [
        (63, ["mapa", "cartograf"]),
        (83, ["pintura", "gravura", "fotografia", "imagem", "charge", "iconograf"]),
        (22, ["jornal", "imprensa", "noticia", "reportagem"]),
        (72, ["propaganda", "anuncio", "cartaz"]),
        (75, ["musica", "cancao", "letra de"]),
        (18, ["literatura", "romance", "poesia", "poema", "cronica"]),
        (48, ["carta"]),
        (93, ["tarefa", "produzir", "escreva", "redija"]),
        (53, ["historiador", "historiograf", "documento"]),
        (28, ["cotidiano", "costumes"]),
        (42, ["politic", "governo", "estado"]),
        (14, ["econom", "comercio", "trabalho"]),
        (7, ["colonia", "colonial"]),
        (55, ["imperio", "imperador", "d. pedro"]),
    ]
    for tag_id, termos in pares:
        if any(t in blob or t in tipos for t in termos):
            candidatos.append(tag_id)
    if candidatos:
        return candidatos[:2]
    if "documento" in blob or "texto" in blob or "imagem" in blob:
        return [53]
    return [53]


def principal():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    tags = {r["id_tag"]: r["tag_nome"] for r in con.execute("SELECT id_tag, tag_nome FROM SKYNET_tag")}
    existentes = set(
        (r["questao_id"], r["tag_id"])
        for r in con.execute("SELECT questao_id, tag_id FROM SKYNET_questao_tags")
    )
    max_id = con.execute("SELECT COALESCE(MAX(id), 0) FROM SKYNET_questao_tags").fetchone()[0]

    itens = {}
    for r in con.execute("SELECT id_questao_id, texto FROM SKYNET_item"):
        itens.setdefault(r["id_questao_id"], []).append(r["texto"] or "")

    docs = {}
    tipos = {}
    for r in con.execute(
        """
        SELECT qd.questao_id, d.nome_documento, d.tipo_documento
        FROM SKYNET_questao_documentos qd
        JOIN SKYNET_documento d ON d.id_documento = qd.documento_id
        """
    ):
        docs.setdefault(r["questao_id"], []).append(r["nome_documento"] or "")
        tipos.setdefault(r["questao_id"], []).append(r["tipo_documento"] or "")

    novas = []
    cobertura = {}
    for q in con.execute("SELECT id_questao, enunciado FROM SKYNET_questao"):
        qid = q["id_questao"]
        texto = (q["enunciado"] or "") + " " + " ".join(itens.get(qid, []))
        docs_nomes = " ".join(docs.get(qid, []))
        docs_tipos = " ".join(tipos.get(qid, []))
        ja = {t for (qq, t) in existentes if qq == qid}
        ids = []
        if not ja:
            ids = inferir_tags(texto, docs_nomes + " " + docs_tipos)
            if not ids:
                ids = fallback(texto, docs_tipos, docs_nomes)
        cobertura[qid] = ja.union(ids)
        for tid in ids:
            if (qid, tid) in existentes:
                continue
            max_id += 1
            novas.append((max_id, qid, tid))
            existentes.add((qid, tid))

    sem = [qid for qid, s in cobertura.items() if not s]
    if sem:
        raise SystemExit("Ainda sem tag: " + str(sem[:20]))

    con.executemany(
        "INSERT INTO SKYNET_questao_tags (id, questao_id, tag_id) VALUES (?, ?, ?)",
        novas,
    )
    con.commit()

    rels = list(
        con.execute(
            "SELECT id, questao_id, tag_id FROM SKYNET_questao_tags ORDER BY questao_id, tag_id, id"
        )
    )
    con.close()

    with open(CSV_QT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id_QT", "id_questao", "id_tag"])
        for i, (pk, qid, tid) in enumerate(rels, start=1):
            w.writerow([i, qid, tid])

    dist = {}
    for _pk, _qid, tid in rels:
        dist[tid] = dist.get(tid, 0) + 1

    print("novas relacoes:", len(novas))
    print("total relacoes:", len(rels))
    print("questoes cobertas:", len(cobertura))
    print("top tags:")
    for tid, n in sorted(dist.items(), key=lambda x: -x[1])[:15]:
        print(f"  {n:4d}  {tags.get(tid)} ({tid})")


if __name__ == "__main__":
    principal()
