#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o arquivo dados.js (window.DADOS = {...}) a partir dos CSVs originais
do projeto Django (pasta ../REPOSITORIO).

Uso:
    python3 gerar_dados.py

Nao precisa de servidor nem de banco de dados: o site estatico le o dados.js.
"""

import csv
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIGEM = os.path.normpath(os.path.join(AQUI, "..", "REPOSITORIO"))

# Encoding de cada arquivo, conforme o popular_banco.py original.
ENCODINGS = {
    "DADOS_EDICAO.csv": "utf-8-sig",
    "DADOS_FASE.csv": "utf-8-sig",
    "DADOS_TIPO_QUESTAO.CSV": "latin-1",
    "DADOS_QUESTAO.csv": "utf-8-sig",
    "DADOS_ITEM.csv": "utf-8-sig",
    "DADOS_DOCUMENTO.csv": "utf-8-sig",
    "DADOS_ANO_HISTORICO.csv": "utf-8-sig",
    "DADOS_TAG.CSV": "latin-1",
    "DADOS_PERIODO.CSV": "latin-1",
    "DADOS_QD.csv": "utf-8-sig",
    "DADOS_QP.csv": "utf-8-sig",
    "DADOS_QT.csv": "latin-1",
    "DADOS_QA.csv": "utf-8-sig",
}


def ler(nome):
    caminho = os.path.join(ORIGEM, nome)
    enc = ENCODINGS.get(nome, "utf-8-sig")
    with open(caminho, mode="r", encoding=enc, newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def limpar(texto):
    """Remove aspas externas e quebras de linha, igual ao importador Django."""
    if texto is None:
        return ""
    t = texto.strip()
    while t.startswith('"') and t.endswith('"') and len(t) >= 2:
        t = t[1:-1].strip()
    return t.replace("\r", "").replace("\n", " ").strip()


def inteiro(valor, padrao=0):
    try:
        return int(str(valor).strip())
    except (ValueError, TypeError, AttributeError):
        return padrao


def principal():
    edicoes = [
        {
            "id": inteiro(l["id_edicao"]),
            "num": inteiro(l["num_edicao"]),
            "ano": inteiro(l["ano_edicao"]),
        }
        for l in ler("DADOS_EDICAO.csv")
        if l.get("id_edicao")
    ]

    fases = [
        {
            "id": inteiro(l["id_fase"]),
            "num": inteiro(l["num_fase"]),
            "tipo": limpar(l["tipo_fase"]),
            "id_edicao": inteiro(l["id_edicao"]),
        }
        for l in ler("DADOS_FASE.csv")
        if l.get("id_fase")
    ]

    tipos = [
        {"id": inteiro(l["id_tipo_questao"]), "nome": limpar(l["tipo_nome"])}
        for l in ler("DADOS_TIPO_QUESTAO.CSV")
        if l.get("id_tipo_questao")
    ]

    questoes = [
        {
            "id": inteiro(l["id_questao"]),
            "num": inteiro(l["num_questao"]),
            "enunciado": limpar(l["enunciado"]),
            "id_fase": inteiro(l["id_fase"]),
            "id_tipo": inteiro(l["id_tipo_questao"]),
        }
        for l in ler("DADOS_QUESTAO.csv")
        if l.get("id_questao")
    ]

    itens = [
        {
            "id": inteiro(l["id_item"]),
            "pontuacao": inteiro(l["pontuacao"]),
            "identificador": limpar(l.get("identificador")),
            "texto": limpar(l.get("texto")),
            "id_questao": inteiro(l["id_questao"]),
        }
        for l in ler("DADOS_ITEM.csv")
        if l.get("id_item")
    ]

    documentos = [
        {
            "id": inteiro(l["id_documento"]),
            "nome": limpar(l["nome_documento"]).replace('""', '"'),
            "tipo": limpar(l["tipo_documento"]),
        }
        for l in ler("DADOS_DOCUMENTO.csv")
        if l.get("id_documento")
    ]

    periodos = [
        {
            "id": inteiro(l["id_periodo"]),
            "nome": limpar(l["periodo_nome"]),
            "seculo": limpar(l["seculo"]),
        }
        for l in ler("DADOS_PERIODO.CSV")
        if l.get("id_periodo")
    ]

    tags = [
        {"id": inteiro(l["id_tag"]), "nome": limpar(l["tag_nome"])}
        for l in ler("DADOS_TAG.CSV")
        if l.get("id_tag")
    ]

    anos = [
        {"id": inteiro(l["id_ano"]), "ano": inteiro(l["ano"])}
        for l in ler("DADOS_ANO_HISTORICO.csv")
        if l.get("id_ano")
    ]

    def relacoes(nome, campo_alvo):
        resultado = []
        for l in ler(nome):
            if l.get("id_questao") and l.get(campo_alvo):
                resultado.append(
                    {
                        "id_questao": inteiro(l["id_questao"]),
                        "alvo": inteiro(l[campo_alvo]),
                    }
                )
        return resultado

    dados = {
        "edicoes": edicoes,
        "fases": fases,
        "tipos": tipos,
        "questoes": questoes,
        "itens": itens,
        "documentos": documentos,
        "periodos": periodos,
        "tags": tags,
        "anos": anos,
        "qd": relacoes("DADOS_QD.csv", "id_documento"),
        "qp": relacoes("DADOS_QP.csv", "id_periodo"),
        "qt": relacoes("DADOS_QT.csv", "id_tag"),
        "qa": relacoes("DADOS_QA.csv", "id_ano"),
    }

    destino = os.path.join(AQUI, "dados.js")
    with open(destino, mode="w", encoding="utf-8") as f:
        f.write("// Arquivo gerado automaticamente por gerar_dados.py\n")
        f.write("// Nao edite a mao. Rode o script apos atualizar os CSVs.\n")
        f.write("window.DADOS = ")
        f.write(json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")

    print("dados.js gerado com sucesso:")
    for chave, valor in dados.items():
        print(f"  {chave}: {len(valor)}")


if __name__ == "__main__":
    principal()
