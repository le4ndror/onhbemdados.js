#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o dados.js a partir de um dump SQL (MySQL ou PostgreSQL) do banco
Django do projeto (tabelas SKYNET_*).

Uso:
    python3 importar_dump.py caminho/para/dump.sql

Recomendado gerar o dump com UMA instrucao INSERT por linha e nomes de
colunas explicitos (veja o README do site). O parser tambem aceita
INSERTs "extended" (varias linhas por instrucao) e sem lista de colunas.
"""

import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Parser de dump SQL
# ---------------------------------------------------------------------------

def remover_comentarios(texto):
    """Remove comentarios -- e /* */ fora de strings."""
    saida = []
    i = 0
    n = len(texto)
    while i < n:
        c = texto[i]
        if c in "'\"":
            # copia a string inteira sem mexer
            quote = c
            saida.append(c)
            i += 1
            while i < n:
                saida.append(texto[i])
                if texto[i] == "\\" and i + 1 < n:
                    saida.append(texto[i + 1])
                    i += 2
                    continue
                if texto[i] == quote:
                    if i + 1 < n and texto[i + 1] == quote:
                        saida.append(texto[i + 1])
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue
        if c == "-" and texto[i:i + 2] == "--":
            while i < n and texto[i] != "\n":
                i += 1
            continue
        if c == "/" and texto[i:i + 2] == "/*":
            i += 2
            while i < n and texto[i:i + 2] != "*/":
                i += 1
            i += 2
            continue
        saida.append(c)
        i += 1
    return "".join(saida)


def dividir_instrucoes(texto):
    """Divide o texto em instrucoes terminadas por ; fora de strings."""
    instrucoes = []
    atual = []
    i = 0
    n = len(texto)
    while i < n:
        c = texto[i]
        if c in "'\"":
            quote = c
            atual.append(c)
            i += 1
            while i < n:
                atual.append(texto[i])
                if texto[i] == "\\" and i + 1 < n:
                    atual.append(texto[i + 1])
                    i += 2
                    continue
                if texto[i] == quote:
                    if i + 1 < n and texto[i + 1] == quote:
                        atual.append(texto[i + 1])
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue
        if c == ";":
            instrucoes.append("".join(atual))
            atual = []
            i += 1
            continue
        atual.append(c)
        i += 1
    if "".join(atual).strip():
        instrucoes.append("".join(atual))
    return instrucoes


def valor_token(texto, pos):
    """Le um valor a partir de pos. Retorna (valor, nova_pos)."""
    n = len(texto)
    # prefixos Postgres: E'...' / B'...' / _binary '...'
    while pos < n and texto[pos] in " \t\r\n":
        pos += 1
    if pos >= n:
        return None, pos

    # prefixo E antes de string
    if texto[pos] in "EeBbXx" and pos + 1 < n and texto[pos + 1] == "'":
        pos += 1

    c = texto[pos]
    if c == "'":
        pos += 1
        buf = []
        while pos < n:
            ch = texto[pos]
            if ch == "\\" and pos + 1 < n:
                nxt = texto[pos + 1]
                mapa = {"n": "\n", "r": "\r", "t": "\t", "0": "\0",
                        "\\": "\\", "'": "'", '"': '"', "b": "\b"}
                buf.append(mapa.get(nxt, nxt))
                pos += 2
                continue
            if ch == "'":
                if pos + 1 < n and texto[pos + 1] == "'":
                    buf.append("'")
                    pos += 2
                    continue
                pos += 1
                break
            buf.append(ch)
            pos += 1
        return "".join(buf), pos

    # NULL
    if texto[pos:pos + 4].upper() == "NULL":
        return None, pos + 4

    # numero / expressao simples ate , ou )
    inicio = pos
    while pos < n and texto[pos] not in ",)":
        pos += 1
    bruto = texto[inicio:pos].strip()
    try:
        return int(bruto), pos
    except ValueError:
        try:
            return float(bruto), pos
        except ValueError:
            return bruto, pos


def parsear_valores(corpo):
    """Recebe '(...),(...)' e retorna lista de tuplas."""
    linhas = []
    pos = 0
    n = len(corpo)
    while pos < n:
        while pos < n and corpo[pos] in " \t\r\n,":
            pos += 1
        if pos >= n:
            break
        if corpo[pos] != "(":
            pos += 1
            continue
        pos += 1
        tupla = []
        while pos < n:
            while pos < n and corpo[pos] in " \t\r\n":
                pos += 1
            if pos < n and corpo[pos] == ")":
                pos += 1
                break
            val, pos = valor_token(corpo, pos)
            tupla.append(val)
            while pos < n and corpo[pos] in " \t\r\n":
                pos += 1
            if pos < n and corpo[pos] == ",":
                pos += 1
                continue
            if pos < n and corpo[pos] == ")":
                pos += 1
                break
        linhas.append(tupla)
    return linhas


IDENT = r'(?:`[^`]+`|"[^"]+"|\[[^\]]+\]|[\w]+)'
RE_INSERT = re.compile(
    r"INSERT\s+INTO\s+(" + IDENT + r"(?:\s*\.\s*" + IDENT + r")*)"
    r"\s*(\([^)]*\))?\s*VALUES\s*(.*)$",
    re.IGNORECASE | re.DOTALL,
)


def normalizar_tabela(nome):
    nome = nome.strip().strip("`\"[]")
    if "." in nome:
        nome = nome.split(".")[-1]
    return nome.strip("`\"[]").lower()


def parsear_colunas(bloco):
    if not bloco:
        return None
    conteudo = bloco.strip()[1:-1]
    cols = []
    for parte in conteudo.split(","):
        cols.append(parte.strip().strip("`\"[]").lower())
    return cols


def parsear_dump(texto):
    texto = remover_comentarios(texto)
    tabelas = {}
    for instrucao in dividir_instrucoes(texto):
        m = RE_INSERT.search(instrucao.strip())
        if not m:
            continue
        tabela = normalizar_tabela(m.group(1))
        colunas = parsear_colunas(m.group(2))
        linhas = parsear_valores(m.group(3))
        tabelas.setdefault(tabela, {"colunas": colunas, "linhas": []})
        destino = tabelas[tabela]
        for tupla in linhas:
            if colunas:
                destino["linhas"].append(dict(zip(colunas, tupla)))
            else:
                destino["linhas"].append(tupla)
    return tabelas


# ---------------------------------------------------------------------------
# Conversao para o formato do site
# ---------------------------------------------------------------------------

def pega(linha, *candidatos, padrao=None):
    if isinstance(linha, dict):
        for c in candidatos:
            if c in linha:
                return linha[c]
        return padrao
    return padrao


def achar_coluna(colunas, *fragmentos):
    if not colunas:
        return None
    for frag in fragmentos:
        for c in colunas:
            if frag in c:
                return c
    return None


def linhas_como_dict(tabela):
    """Garante dicts mesmo quando o INSERT nao trazia nomes de colunas."""
    info = tabela
    if info["colunas"]:
        return info["linhas"], info["colunas"]
    return info["linhas"], None


def inteiro(v, padrao=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return padrao


def montar_m2m(info, fragmento_alvo):
    linhas, colunas = info["linhas"], info["colunas"]
    resultado = []
    for linha in linhas:
        if isinstance(linha, dict):
            c_questao = achar_coluna(list(linha.keys()), "questao")
            c_alvo = achar_coluna(list(linha.keys()), fragmento_alvo)
            if c_questao and c_alvo:
                resultado.append(
                    {"id_questao": inteiro(linha[c_questao]),
                     "alvo": inteiro(linha[c_alvo])}
                )
        elif colunas:
            c_questao = achar_coluna(colunas, "questao")
            c_alvo = achar_coluna(colunas, fragmento_alvo)
            if c_questao and c_alvo:
                idx_q = colunas.index(c_questao)
                idx_a = colunas.index(c_alvo)
                resultado.append(
                    {"id_questao": inteiro(linha[idx_q]),
                     "alvo": inteiro(linha[idx_a])}
                )
    return resultado


def construir(tabelas):
    def info(nome):
        return tabelas.get(nome, {"colunas": None, "linhas": []})

    t_ed = info("skynet_edicao")
    edicoes = []
    for l in t_ed["linhas"]:
        edicoes.append({
            "id": inteiro(pega(l, "id_edicao")),
            "num": inteiro(pega(l, "num_edicao")),
            "ano": inteiro(pega(l, "ano_edicao")),
        })

    t_fa = info("skynet_fase")
    fases = []
    for l in t_fa["linhas"]:
        fases.append({
            "id": inteiro(pega(l, "id_fase")),
            "num": inteiro(pega(l, "num_fase")),
            "tipo": pega(l, "tipo_fase", padrao="") or "",
            "id_edicao": inteiro(pega(l, "id_edicao_id", "id_edicao")),
        })

    t_tp = info("skynet_tipo_questao")
    tipos = []
    for l in t_tp["linhas"]:
        tipos.append({
            "id": inteiro(pega(l, "id_tipo_questao")),
            "nome": pega(l, "tipo_nome", padrao="") or "",
        })

    t_q = info("skynet_questao")
    questoes = []
    for l in t_q["linhas"]:
        questoes.append({
            "id": inteiro(pega(l, "id_questao")),
            "num": inteiro(pega(l, "num_questao")),
            "enunciado": pega(l, "enunciado", padrao="") or "",
            "id_fase": inteiro(pega(l, "id_fase_id", "id_fase")),
            "id_tipo": inteiro(pega(l, "id_tipo_questao_id", "id_tipo_questao")),
        })

    t_i = info("skynet_item")
    itens = []
    for l in t_i["linhas"]:
        itens.append({
            "id": inteiro(pega(l, "id_item")),
            "pontuacao": inteiro(pega(l, "pontuacao")),
            "identificador": str(pega(l, "identificador", padrao="") or ""),
            "texto": pega(l, "texto", padrao="") or "",
            "id_questao": inteiro(pega(l, "id_questao_id", "id_questao")),
        })

    t_d = info("skynet_documento")
    documentos = []
    for l in t_d["linhas"]:
        documentos.append({
            "id": inteiro(pega(l, "id_documento")),
            "nome": pega(l, "nome_documento", padrao="") or "",
            "tipo": pega(l, "tipo_documento", padrao="") or "",
        })

    t_p = info("skynet_periodo")
    periodos = []
    for l in t_p["linhas"]:
        periodos.append({
            "id": inteiro(pega(l, "id_periodo")),
            "nome": pega(l, "periodo_nome", padrao="") or "",
            "seculo": str(pega(l, "seculo", padrao="") or ""),
        })

    t_tg = info("skynet_tag")
    tags = []
    for l in t_tg["linhas"]:
        tags.append({
            "id": inteiro(pega(l, "id_tag")),
            "nome": pega(l, "tag_nome", padrao="") or "",
        })

    t_a = info("skynet_ano_historico")
    anos = []
    for l in t_a["linhas"]:
        anos.append({
            "id": inteiro(pega(l, "id_ano")),
            "ano": inteiro(pega(l, "ano")),
        })

    return {
        "edicoes": edicoes,
        "fases": fases,
        "tipos": tipos,
        "questoes": questoes,
        "itens": itens,
        "documentos": documentos,
        "periodos": periodos,
        "tags": tags,
        "anos": anos,
        "qd": montar_m2m(info("skynet_questao_documentos"), "documento"),
        "qp": montar_m2m(info("skynet_questao_periodos"), "periodo"),
        "qt": montar_m2m(info("skynet_questao_tags"), "tag"),
        "qa": montar_m2m(info("skynet_questao_anos"), "ano"),
    }


def principal():
    if len(sys.argv) < 2:
        print("Uso: python3 importar_dump.py caminho/para/dump.sql")
        sys.exit(1)
    caminho = sys.argv[1]
    if not os.path.exists(caminho):
        print(f"Arquivo nao encontrado: {caminho}")
        sys.exit(1)

    with open(caminho, mode="r", encoding="utf-8", errors="replace") as f:
        texto = f.read()

    tabelas = parsear_dump(texto)
    dados = construir(tabelas)

    destino = os.path.join(AQUI, "dados.js")
    with open(destino, mode="w", encoding="utf-8") as f:
        f.write("// Arquivo gerado automaticamente por importar_dump.py\n")
        f.write("window.DADOS = ")
        f.write(json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")

    print(f"dados.js gerado a partir de: {caminho}")
    for chave, valor in dados.items():
        print(f"  {chave}: {len(valor)}")


if __name__ == "__main__":
    principal()
