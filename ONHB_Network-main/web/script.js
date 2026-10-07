/* Repositorio SKYNET - versao estatica (HTML/CSS/JS)
   Traduzido do projeto Django original. Os dados ficam em dados.js. */

(function () {
    "use strict";

    var dados = window.DADOS || {};

    /* ---------------- Utilitarios ---------------- */

    function esc(valor) {
        return String(valor == null ? "" : valor)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function porId(lista) {
        var mapa = new Map();
        (lista || []).forEach(function (item) {
            mapa.set(item.id, item);
        });
        return mapa;
    }

    /* Converte relacoes [{id_questao, alvo}] em Map questaoId -> [objeto] */
    function montarRelacoes(relacoes, lookup) {
        var mapa = new Map();
        (relacoes || []).forEach(function (rel) {
            var alvo = lookup.get(rel.alvo);
            if (!alvo) return;
            if (!mapa.has(rel.id_questao)) mapa.set(rel.id_questao, []);
            mapa.get(rel.id_questao).push(alvo);
        });
        return mapa;
    }

    var edicaoById = porId(dados.edicoes);
    var faseById = porId(dados.fases);
    var tipoById = porId(dados.tipos);
    var questaoById = porId(dados.questoes);
    var documentoById = porId(dados.documentos);
    var periodoById = porId(dados.periodos);
    var tagById = porId(dados.tags);
    var anoById = porId(dados.anos);

    var qDocumentos = montarRelacoes(dados.qd, documentoById);
    var qPeriodos = montarRelacoes(dados.qp, periodoById);
    var qTags = montarRelacoes(dados.qt, tagById);
    var qAnos = montarRelacoes(dados.qa, anoById);

    var questoesPorFase = new Map();
    (dados.questoes || []).forEach(function (q) {
        if (!questoesPorFase.has(q.id_fase)) questoesPorFase.set(q.id_fase, []);
        questoesPorFase.get(q.id_fase).push(q);
    });
    questoesPorFase.forEach(function (lista) {
        lista.sort(function (a, b) { return a.num - b.num; });
    });

    var itensPorQuestao = new Map();
    (dados.itens || []).forEach(function (item) {
        if (!itensPorQuestao.has(item.id_questao)) itensPorQuestao.set(item.id_questao, []);
        itensPorQuestao.get(item.id_questao).push(item);
    });
    itensPorQuestao.forEach(function (lista) {
        lista.sort(function (a, b) {
            return String(a.identificador).localeCompare(String(b.identificador));
        });
    });

    var fasesPorEdicao = new Map();
    (dados.fases || []).forEach(function (f) {
        if (!fasesPorEdicao.has(f.id_edicao)) fasesPorEdicao.set(f.id_edicao, []);
        fasesPorEdicao.get(f.id_edicao).push(f);
    });
    fasesPorEdicao.forEach(function (lista) {
        lista.sort(function (a, b) { return a.num - b.num; });
    });

    function contem(texto, agulha) {
        return String(texto == null ? "" : texto)
            .toLowerCase()
            .indexOf(String(agulha).toLowerCase()) !== -1;
    }

    function igual(a, b) {
        return String(a == null ? "" : a).toLowerCase() ===
            String(b == null ? "" : b).toLowerCase();
    }

    function truncarPalavras(texto, limite) {
        var palavras = String(texto || "").split(/\s+/);
        if (palavras.length <= limite) return texto;
        return palavras.slice(0, limite).join(" ") + " ...";
    }

    function listaUnica(valores) {
        var vistos = {};
        var resultado = [];
        valores.forEach(function (v) {
            if (!v) return;
            if (vistos[v]) return;
            vistos[v] = true;
            resultado.push(v);
        });
        return resultado;
    }

    /* ---------------- Filtro de questoes ---------------- */

    function filtrarQuestoes(lista, f, opcoes) {
        opcoes = opcoes || {};
        return lista.filter(function (q) {
            if (f.documento) {
                var docs = qDocumentos.get(q.id) || [];
                var achou = docs.some(function (d) { return contem(d.nome, f.documento); });
                if (!achou) return false;
            }
            if (f.tipo) {
                var tipo = tipoById.get(q.id_tipo);
                var nome = tipo ? tipo.nome : "";
                if (opcoes.tipoExato ? !igual(nome, f.tipo) : !contem(nome, f.tipo)) return false;
            }
            if (f.ano) {
                var anos = qAnos.get(q.id) || [];
                var achouAno = anos.some(function (a) { return contem(String(a.ano), f.ano); });
                if (!achouAno) return false;
            }
            if (f.tag) {
                var tags = qTags.get(q.id) || [];
                var achouTag = tags.some(function (t) { return contem(t.nome, f.tag); });
                if (!achouTag) return false;
            }
            if (f.periodo) {
                var periodos = qPeriodos.get(q.id) || [];
                var achouPeriodo = periodos.some(function (p) {
                    return opcoes.periodoExato ? igual(p.nome, f.periodo) : contem(p.nome, f.periodo);
                });
                if (!achouPeriodo) return false;
            }
            if (f.enunciado && !contem(q.enunciado, f.enunciado)) return false;
            return true;
        });
    }

    /* ---------------- Helpers de HTML ---------------- */

    function opcoes(lista, selecionado, rotuloTodos) {
        var html = '<option value="">' + esc(rotuloTodos) + "</option>";
        lista.forEach(function (valor) {
            var sel = selecionado === valor ? " selected" : "";
            html += '<option value="' + esc(valor) + '"' + sel + ">" + esc(valor) + "</option>";
        });
        return html;
    }

    function vazio(mensagem) {
        return '<p class="msg-vazio">' + mensagem + "</p>";
    }

    function naoEncontrado() {
        return '<div class="main-container"><section class="info-section">' +
            "<h3>Conteudo nao encontrado</h3>" +
            '<p>O item solicitado nao existe na base de dados.</p>' +
            '<p><a class="voltar-topo" href="#/">&larr; Voltar para o inicio</a></p>' +
            "</section></div>";
    }

    /* ---------------- Telas ---------------- */

    function renderEdicoes() {
        var edicoes = (dados.edicoes || []).slice().sort(function (a, b) {
            return b.ano - a.ano;
        });

        var html = '<div class="main-container">' +
            '<section class="banner-boas-vindas">' +
            '<div class="banner-texto">' +
            "<h2>PAGINA INICIAL DO REPOSITORIO</h2>" +
            "<p>Bem-vindo ao portal unificado de questoes da Olimpiada Nacional em " +
            "Historia do Brasil. Explore todas as edicoes passadas e aprofunde seu " +
            "conhecimento.</p></div>" +
            '<div class="banner-ilustracao">&#128214;&#128220;</div>' +
            "</section>" +
            '<div class="secao-titulo"><h2>Visualizar qualquer questao</h2>' +
            '<a href="#/busca">&larr; Busca Global</a></div>' +
            '<div class="secao-titulo"><h2>Selecione uma Edicao</h2></div>' +
            '<section class="container-edicoes">';

        if (!edicoes.length) {
            html += vazio("Nenhuma edicao encontrada no banco de dados.");
        } else {
            edicoes.forEach(function (e) {
                html += '<div class="card-edicao">' +
                    '<div class="card-icon">&#128214;</div>' +
                    '<div class="card-info">' +
                    "<h3>" + esc(e.num) + "a Edicao</h3>" +
                    '<p class="ano-edicao">Ano: ' + esc(e.ano) + "</p>" +
                    '<a class="btn-acessar" href="#/edicao/' + e.id + '">Acessar Edicao &rarr;</a>' +
                    "</div></div>";
            });
        }

        html += "</section>" +
            '<div class="instrucao-rodape">&rarr; CLIQUE EM UMA DAS EDIÇÕES ACIMA ' +
            "PARA COMEÇAR A EXPLORAR AS QUESTÕES.</div></div>";

        return html;
    }

    function renderFases(edicaoId) {
        var edicao = edicaoById.get(Number(edicaoId));
        if (!edicao) return naoEncontrado();

        var fases = fasesPorEdicao.get(edicao.id) || [];

        var html = '<div class="main-container">' +
            '<div class="topo-fases">' +
            '<div class="titulos-fases"><h2>PAGINA DA EDIÇAO: ' + esc(edicao.num) +
            "a Ediçao (" + esc(edicao.ano) + ")</h2><span>- Selecione a Fase</span></div>" +
            '<a class="btn-voltar" href="#/">VOLTAR PARA TODAS AS EDIÇÕES</a>' +
            "</div>" +
            '<div class="faixa-secao">FASES DA EDIÇAO</div>' +
            '<section class="banner-boas-vindas banner-fase">' +
            '<div class="banner-ilustracao">&#128220;</div>' +
            '<div class="banner-texto text-center">' +
            "<h2>" + esc(edicao.num) + "a EDIÇAO (" + esc(edicao.ano) + ")</h2>" +
            "<p>Fases da Olimpiada Nacional em Historia do Brasil da " +
            esc(edicao.num) + "a ediçao, organizadas em ordem cronologica de " +
            "aplicaçao.</p></div>" +
            '<div class="banner-ilustracao">&#129517;</div>' +
            "</section>" +
            '<section class="container-fases">';

        if (!fases.length) {
            html += vazio("Nenhuma fase cadastrada para esta ediçao no banco de dados.");
        } else {
            fases.forEach(function (f) {
                var trofeu = contem(f.tipo, "Final") || contem(f.tipo, "Grande");
                html += '<a class="card-fase" href="#/fase/' + f.id + '">' +
                    '<div class="card-fase-icon">' + (trofeu ? "&#127942;" : "&#128214;") + "</div>" +
                    '<div class="card-fase-info">' +
                    "<h3>" + esc(f.num) + ". FASE " + esc(f.num) + "</h3>" +
                    "<p>" + esc(f.tipo) + "</p></div></a>";
            });
        }

        html += "</section></div>";
        return html;
    }

    function renderQuestoes(faseId, params) {
        var fase = faseById.get(Number(faseId));
        if (!fase) return naoEncontrado();
        var edicao = edicaoById.get(fase.id_edicao);

        var filtros = {
            documento: params.get("documento") || "",
            tipo: params.get("tipos") || "",
            ano: params.get("anos") || "",
            tag: params.get("tags") || "",
            periodo: params.get("periodos") || ""
        };

        var lista = questoesPorFase.get(fase.id) || [];
        var resultado = filtrarQuestoes(lista, filtros, { tipoExato: true, periodoExato: true });

        var tiposDisponiveis = listaUnica(dados.questoes.map(function (q) {
            var t = tipoById.get(q.id_tipo);
            return t ? t.nome : "";
        }));
        var periodosDisponiveis = listaUnica(dados.periodos.map(function (p) { return p.nome; }));

        var html = '<div class="main-container">' +
            '<div class="faixa-secao">PLATAFORMA SKYNET</div>' +
            '<div class="secao-titulo"><h2>Ediçao ' +
            esc(edicao ? edicao.num : "?") + " | Fase " + esc(fase.num) +
            " (" + esc(fase.tipo) + ")</h2>" +
            '<a class="btn-voltar" href="#/edicao/' + fase.id_edicao +
            '">&larr; Voltar para as Fases</a></div>' +
            "<p>Abaixo estao as questoes desta fase:</p>" +
            '<form class="form-filtros" id="filtro-fase">' +
            '<input class="input-busca" type="text" name="documento" placeholder="Pesquise por Documento..." value="' +
            esc(filtros.documento) + '">' +
            '<select class="select-filtro" name="tipos" onchange="this.form.requestSubmit()">' +
            opcoes(tiposDisponiveis, filtros.tipo, "Tipo de Questao (Todos)") + "</select>" +
            '<input class="input-busca" type="text" name="anos" placeholder="Pesquise por ano..." value="' +
            esc(filtros.ano) + '">' +
            '<input class="input-busca" type="text" name="tags" placeholder="Pesquise por tags..." value="' +
            esc(filtros.tag) + '">' +
            '<select class="select-filtro" name="periodos" onchange="this.form.requestSubmit()">' +
            opcoes(periodosDisponiveis, filtros.periodo, "Periodos (Todos)") + "</select>" +
            '<button type="submit" class="btn-buscar">&#128269; FILTRAR QUESTOES</button>' +
            "</form>" +
            '<section class="container-questoes">';

        if (!resultado.length) {
            html += vazio("Nenhuma questao encontrada para esta fase.");
        } else {
            resultado.forEach(function (q) {
                var tipo = tipoById.get(q.id_tipo);
                html += '<div class="card-questao">' +
                    "<h3>Questao " + esc(q.num) + "</h3>" +
                    "<p><strong>Tipo:</strong> " + esc(tipo ? tipo.nome : "") + "</p>" +
                    "<p><strong>Enunciado:</strong> " + esc(q.enunciado) + "</p>" +
                    '<a class="btn-detalhes" href="#/questao/' + q.id +
                    '">Ver alternativas e detalhes</a>' +
                    "</div>";
            });
        }

        html += "</section>" +
            '<div class="rodape-nav"><a href="#/edicao/' + fase.id_edicao +
            '">&larr; Voltar para as Fases</a></div></div>';

        return html;
    }

    function renderQuestao(questaoId) {
        var q = questaoById.get(Number(questaoId));
        if (!q) return naoEncontrado();

        var fase = faseById.get(q.id_fase);
        var edicao = fase ? edicaoById.get(fase.id_edicao) : null;
        var tipo = tipoById.get(q.id_tipo);
        var itens = itensPorQuestao.get(q.id) || [];
        var documentos = qDocumentos.get(q.id) || [];
        var periodos = qPeriodos.get(q.id) || [];
        var tags = qTags.get(q.id) || [];
        var anos = qAnos.get(q.id) || [];

        var html = '<div class="main-container">' +
            '<div class="faixa-secao">PLATAFORMA SKYNET</div>' +
            '<div class="secao-titulo"><h2>Questao ' + esc(q.num) + "</h2>" +
            '<a class="btn-voltar" href="#/fase/' + q.id_fase +
            '">&larr; Voltar para as Questoes desta Fase</a></div>' +
            '<p><strong>Ediçao:</strong> ' + esc(edicao ? edicao.num : "?") +
            " | <strong>Fase:</strong> " + esc(fase ? fase.num : "?") +
            " | <strong>Tipo:</strong> " + esc(tipo ? tipo.nome : "") + "</p>" +
            '<section class="bloco-enunciado"><h2>Questao ' + esc(q.num) + "</h2>" +
            "<p>" + esc(q.enunciado) + "</p></section>";

        html += infoSection("&#128196; Documentos de Apoio", documentos.map(function (d) {
            return "<li><strong>[" + esc(d.tipo) + "]</strong> " + esc(d.nome) + "</li>";
        }), "Nenhum documento associado a esta questao.");

        html += infoSection("&#128196; Periodos", periodos.map(function (p) {
            return "<li><strong>[" + esc(p.seculo) + "]</strong> " + esc(p.nome) + "</li>";
        }), "Nenhum periodo associado a esta questao.");

        html += infoSection("&#128196; Tags", tags.map(function (t) {
            return "<li>" + esc(t.nome) + "</li>";
        }), "Nenhuma tag associada a esta questao.");

        html += infoSection("&#128196; Anos Historicos", anos.map(function (a) {
            return "<li>" + esc(a.ano) + "</li>";
        }), "Nenhum ano historico associado a esta questao.");

        html += '<section class="bloco-alternativas"><h3>Alternativas / Itens cadastrados:</h3>';

        if (!itens.length) {
            html += vazio("Nenhuma alternativa (ITEM) populada para esta questao ainda.");
        } else {
            itens.forEach(function (item) {
                html += '<div class="card-alternativa">' +
                    '<div class="cabecalho">' +
                    "<span><strong>Letra/ID:</strong> " + esc(item.identificador) + "</span>" +
                    '<span class="pontuacao-badge">' + esc(item.pontuacao) + " pontos</span>" +
                    "</div>" +
                    '<p class="texto">' + esc(item.texto) + "</p>" +
                    "</div>";
            });
        }

        html += "</section>" +
            '<div class="rodape-nav"><a href="#/fase/' + q.id_fase +
            '">&larr; Voltar para as Questoes desta Fase</a></div></div>';

        return html;
    }

    function infoSection(titulo, itensHtml, mensagemVazia) {
        var html = '<section class="info-section"><h3>' + titulo + "</h3>";
        if (!itensHtml.length) {
            html += '<p class="vazio">' + mensagemVazia + "</p>";
        } else {
            html += "<ul>" + itensHtml.join("") + "</ul>";
        }
        return html + "</section>";
    }

    function renderBusca(params) {
        var filtros = {
            documento: params.get("documento") || "",
            enunciado: params.get("enunciado") || "",
            tipo: params.get("tipos") || "",
            ano: params.get("anos") || "",
            tag: params.get("tags") || "",
            periodo: params.get("periodos") || ""
        };

        var resultado = filtrarQuestoes(dados.questoes, filtros, {
            tipoExato: true,
            periodoExato: true
        });

        var tiposDisponiveis = listaUnica(dados.tipos.map(function (t) { return t.nome; }));
        var periodosDisponiveis = listaUnica(dados.periodos.map(function (p) { return p.nome; }));

        var html = '<div class="main-container">' +
            '<div class="faixa-secao">REPOSITORIO SKYNET - BUSCA GLOBAL</div>' +
            "<p>Pesquise questoes em todas as ediçoes e fases registradas no banco de dados.</p>" +
            '<form class="form-filtros" id="filtro-busca">' +
            '<input class="input-busca" type="text" name="documento" placeholder="Documento..." value="' +
            esc(filtros.documento) + '">' +
            '<input class="input-busca" type="text" name="enunciado" placeholder="Enunciado..." value="' +
            esc(filtros.enunciado) + '">' +
            '<select class="select-filtro" name="tipos">' +
            opcoes(tiposDisponiveis, filtros.tipo, "Tipo (Todos)") + "</select>" +
            '<input class="input-busca" type="text" name="anos" placeholder="Ano Historico..." value="' +
            esc(filtros.ano) + '">' +
            '<input class="input-busca" type="text" name="tags" placeholder="Tags..." value="' +
            esc(filtros.tag) + '">' +
            '<select class="select-filtro" name="periodos">' +
            opcoes(periodosDisponiveis, filtros.periodo, "Periodos (Todos)") + "</select>" +
            '<button type="submit" class="btn-buscar">&#128269; FILTRAR QUESTOES</button>' +
            "</form>" +
            '<div><a class="voltar-topo" href="#/">&larr; Voltar para a Pagina Inicial</a></div>' +
            '<section class="container-questoes">';

        if (!resultado.length) {
            html += vazio("Nenhuma questao encontrada com os filtros selecionados.");
        } else {
            resultado.slice(0, 500).forEach(function (q) {
                var fase = faseById.get(q.id_fase);
                var edicao = fase ? edicaoById.get(fase.id_edicao) : null;
                var tipo = tipoById.get(q.id_tipo);
                html += '<div class="card-questao">' +
                    "<div>" +
                    '<span class="badge-info">Ediçao ' + esc(edicao ? edicao.num : "?") +
                    "a (" + esc(edicao ? edicao.ano : "?") + ")</span>" +
                    '<span class="badge-info">Fase ' + esc(fase ? fase.num : "?") + "</span>" +
                    '<span class="badge-info">Tipo: ' + esc(tipo ? tipo.nome : "") + "</span>" +
                    "</div>" +
                    "<h3>Questao " + esc(q.num) + "</h3>" +
                    '<p><strong>Enunciado:</strong> ' +
                    esc(truncarPalavras(q.enunciado, 30)) + "</p>" +
                    '<a class="btn-detalhes" href="#/questao/' + q.id +
                    '">Ver detalhes da questao &rarr;</a>' +
                    "</div>";
            });
            if (resultado.length > 500) {
                html += '<p class="msg-vazio">Mostrando as primeiras 500 de ' +
                    resultado.length + " questoes. Refine os filtros para ver outras.</p>";
            }
        }

        html += "</section></div>";
        return html;
    }

    /* ---------------- Roteamento ---------------- */

    var app = document.getElementById("app");

    function parseHash() {
        var bruto = location.hash.replace(/^#/, "");
        if (!bruto) bruto = "/";
        var partes = bruto.split("?");
        var caminho = partes[0];
        var params = new URLSearchParams(partes[1] || "");
        var segmentos = caminho.split("/").filter(Boolean);
        return { segmentos: segmentos, params: params };
    }

    function configurarFormulario(idFormulario, prefixoHash) {
        var form = document.getElementById(idFormulario);
        if (!form) return;
        form.addEventListener("submit", function (evento) {
            evento.preventDefault();
            var dadosForm = new FormData(form);
            var query = new URLSearchParams();
            dadosForm.forEach(function (valor, chave) {
                if (valor) query.set(chave, valor);
            });
            var sufixo = query.toString();
            location.hash = prefixoHash + (sufixo ? "?" + sufixo : "");
        });
    }

    function render() {
        var rota = parseHash();
        var seg = rota.segmentos;
        var html;

        if (seg.length === 0) {
            html = renderEdicoes();
        } else if (seg[0] === "edicao" && seg[1]) {
            html = renderFases(seg[1]);
        } else if (seg[0] === "fase" && seg[1]) {
            html = renderQuestoes(seg[1], rota.params);
        } else if (seg[0] === "questao" && seg[1]) {
            html = renderQuestao(seg[1]);
        } else if (seg[0] === "busca") {
            html = renderBusca(rota.params);
        } else {
            html = naoEncontrado();
        }

        app.innerHTML = html;

        if (seg[0] === "fase" && seg[1]) {
            configurarFormulario("filtro-fase", "#/fase/" + seg[1]);
        } else if (seg[0] === "busca") {
            configurarFormulario("filtro-busca", "#/busca");
        }

        window.scrollTo(0, 0);
    }

    window.addEventListener("hashchange", render);

    if (!location.hash) location.hash = "#/";
    render();
})();
