#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o dados.js a partir de um banco SQLite do Django (db.sqlite3),
sem precisar do Django instalado.

Uso:
    python3 importar_sqlite.py caminho/para/db.sqlite3

Se nenhum caminho for informado, usa ../REPOSITORIO/db.sqlite3

Regenera o mesmo conjunto de dados que gerar_dados.py (via CSVs), porem
lendo direto das tabelas SKYNET_* do banco.
"""

import json
import os
import sqlite3
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PADRAO = os.path.normpath(os.path.join(AQUI, "..", "REPOSITORIO", "db.sqlite3"))


def buscar(con, sql):
    con.row_factory = sqlite3.Row
    return [dict(r) for r in con.execute(sql).fetchall()]


def principal():
    caminho = sys.argv[1] if len(sys.argv) > 1 else PADRAO
    if not os.path.exists(caminho):
        print(f"Banco nao encontrado: {caminho}")
        sys.exit(1)

    con = sqlite3.connect(caminho)

    edicoes = [
        {"id": r["id_edicao"], "num": r["num_edicao"], "ano": r["ano_edicao"]}
        for r in buscar(con, "SELECT id_edicao, num_edicao, ano_edicao FROM SKYNET_edicao")
    ]
    fases = [
        {
            "id": r["id_fase"],
            "num": r["num_fase"],
            "tipo": r["tipo_fase"],
            "id_edicao": r["id_edicao_id"],
        }
        for r in buscar(
            con, "SELECT id_fase, num_fase, tipo_fase, id_edicao_id FROM SKYNET_fase"
        )
    ]
    tipos = [
        {"id": r["id_tipo_questao"], "nome": r["tipo_nome"]}
        for r in buscar(
            con, "SELECT id_tipo_questao, tipo_nome FROM SKYNET_tipo_questao"
        )
    ]
    questoes = [
        {
            "id": r["id_questao"],
            "num": r["num_questao"],
            "enunciado": r["enunciado"],
            "id_fase": r["id_fase_id"],
            "id_tipo": r["id_tipo_questao_id"],
        }
        for r in buscar(
            con,
            "SELECT id_questao, num_questao, enunciado, id_fase_id, "
            "id_tipo_questao_id FROM SKYNET_questao",
        )
    ]
    itens = [
        {
            "id": r["id_item"],
            "pontuacao": r["pontuacao"],
            "identificador": r["identificador"],
            "texto": r["texto"],
            "id_questao": r["id_questao_id"],
        }
        for r in buscar(
            con,
            "SELECT id_item, pontuacao, identificador, texto, id_questao_id "
            "FROM SKYNET_item",
        )
    ]
    documentos = [
        {
            "id": r["id_documento"],
            "nome": r["nome_documento"],
            "tipo": r["tipo_documento"],
        }
        for r in buscar(
            con,
            "SELECT id_documento, nome_documento, tipo_documento FROM SKYNET_documento",
        )
    ]
    periodos = [
        {"id": r["id_periodo"], "nome": r["periodo_nome"], "seculo": r["seculo"]}
        for r in buscar(
            con, "SELECT id_periodo, periodo_nome, seculo FROM SKYNET_periodo"
        )
    ]
    tags = [
        {"id": r["id_tag"], "nome": r["tag_nome"]}
        for r in buscar(con, "SELECT id_tag, tag_nome FROM SKYNET_tag")
    ]
    anos = [
        {"id": r["id_ano"], "ano": r["ano"]}
        for r in buscar(con, "SELECT id_ano, ano FROM SKYNET_ano_historico")
    ]

    # Tabelas ManyToMany (auto-geradas pelo Django)
    qd = buscar(
        con,
        "SELECT questao_id AS id_questao, documento_id AS alvo "
        "FROM SKYNET_questao_documentos",
    )
    qp = buscar(
        con,
        "SELECT questao_id AS id_questao, periodo_id AS alvo "
        "FROM SKYNET_questao_periodos",
    )
    qt = buscar(
        con, "SELECT questao_id AS id_questao, tag_id AS alvo FROM SKYNET_questao_tags"
    )
    qa = buscar(
        con,
        "SELECT questao_id AS id_questao, ano_historico_id AS alvo "
        "FROM SKYNET_questao_anos",
    )

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
        "qd": qd,
        "qp": qp,
        "qt": qt,
        "qa": qa,
    }

    destino = os.path.join(AQUI, "dados.js")
    with open(destino, mode="w", encoding="utf-8") as f:
        f.write("// Arquivo gerado automaticamente por importar_sqlite.py\n")
        f.write("window.DADOS = ")
        f.write(json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
        f.write(";\n")

    con.close()
    print(f"dados.js gerado a partir de: {caminho}")
    for chave, valor in dados.items():
        print(f"  {chave}: {len(valor)}")


if __name__ == "__main__":
    principal()
