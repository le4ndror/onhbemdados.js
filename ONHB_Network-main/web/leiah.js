/* LEIAH - Repositorio de Questoes de Historia e ONHB
   Consome window.DADOS (dados.js) gerado a partir do acervo. */

/* ================= Dados ================= */

var D = window.DADOS || {};

function indexar(lista) {
  var m = new Map();
  (lista || []).forEach(function (o) { m.set(o.id, o); });
  return m;
}

function agrupar(relacoes, lookup) {
  var m = new Map();
  (relacoes || []).forEach(function (r) {
    var alvo = lookup.get(r.alvo);
    if (!alvo) return;
    if (!m.has(r.id_questao)) m.set(r.id_questao, []);
    m.get(r.id_questao).push(alvo);
  });
  return m;
}

var edicaoById = indexar(D.edicoes);
var faseById = indexar(D.fases);
var tipoById = indexar(D.tipos);
var docById = indexar(D.documentos);
var perById = indexar(D.periodos);
var tagById = indexar(D.tags);

var qDocumentos = agrupar(D.qd, docById);
var qPeriodos = agrupar(D.qp, perById);
var qTags = agrupar(D.qt, tagById);
var qAnos = (function () {
  var anoById = indexar(D.anos);
  return agrupar(D.qa, anoById);
})();

var itensPorQuestao = (function () {
  var m = new Map();
  (D.itens || []).forEach(function (i) {
    if (!m.has(i.id_questao)) m.set(i.id_questao, []);
    m.get(i.id_questao).push(i);
  });
  m.forEach(function (arr) {
    arr.sort(function (a, b) {
      return String(a.identificador).localeCompare(String(b.identificador));
    });
  });
  return m;
})();

function esc(valor) {
  return String(valor == null ? "" : valor)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function unico(arr) {
  var vistos = {};
  return arr.filter(function (v) {
    if (v == null || v === "" || vistos[v]) return false;
    vistos[v] = true;
    return true;
  });
}

var PERIODO_DISPLAY = {
  Colonial: "Brasil Colonial",
  Imperial: "Brasil Império",
  Republicano: "Brasil República",
  Republlicano: "Brasil República"
};

function periodoLabel(nome) {
  return PERIODO_DISPLAY[nome] || nome;
}

function faseLabel(f) {
  if (!f) return "Fase";
  var t = f.tipo || "";
  if (/final/i.test(t)) return "Fase Final";
  if (/desafio/i.test(t)) return "Desafio";
  if (/introdut/i.test(t)) return "Fase Introdutória";
  return f.num + "ª fase";
}

function seculoParaAno(sec) {
  var n = parseInt(sec, 10);
  if (isNaN(n)) return null;
  return (n - 1) * 100 + 50;
}

var QUESTIONS_DATA = (D.questoes || []).map(function (q) {
  var fase = faseById.get(q.id_fase);
  var edicao = fase ? edicaoById.get(fase.id_edicao) : null;
  var tipo = tipoById.get(q.id_tipo);
  var docs = qDocumentos.get(q.id) || [];
  var pers = qPeriodos.get(q.id) || [];
  var tgs = qTags.get(q.id) || [];
  var ans = qAnos.get(q.id) || [];
  var itens = itensPorQuestao.get(q.id) || [];

  var anosList = ans.map(function (a) { return a.ano; })
    .filter(function (n) { return !isNaN(n); })
    .sort(function (a, b) { return a - b; });

  var year = anosList.length ? anosList[0] : null;
  if (year == null && pers.length) year = seculoParaAno(pers[0].seculo);

  var periodNames = unico(pers.map(function (p) { return p.nome; }));
  var docTipos = unico(docs.map(function (d) { return d.tipo; }));
  var docNomes = unico(docs.map(function (d) { return d.nome; }));
  var tagNames = unico(tgs.map(function (t) { return t.nome; }));

  var edicaoAno = edicao ? edicao.ano : null;
  var edicaoNum = edicao ? edicao.num : null;
  var tipoNome = tipo ? tipo.nome : "";
  var phase = faseLabel(fase);
  var edition = edicao ? edicaoAno + " (" + edicaoNum + "ª Edição)" : "Sem edição";

  var date = anosList.length
    ? anosList.join(", ")
    : (pers.length ? pers.map(function (p) { return p.seculo + "00"; }).join(", ")
      : "Datação não informada");

  var descFull = q.enunciado || "";
  var itemText = itens.map(function (i) { return i.texto; }).join(" ");

  var searchText = [
    descFull, itemText, docNomes.join(" "), docTipos.join(" "),
    tagNames.join(" "), periodNames.join(" "),
    periodNames.map(periodoLabel).join(" "),
    tipoNome, edition, phase, "questao " + q.num, "questão " + q.num
  ].join(" ").toLowerCase();

  return {
    id: q.id,
    num: q.num,
    headline: "Questão " + q.num + " · " + (tipoNome || "Questão"),
    title: descFull.length > 90 ? descFull.slice(0, 90) + "…" : descFull,
    desc: descFull,
    descShort: descFull.length > 150 ? descFull.slice(0, 150) + "…" : descFull,
    edition: edition,
    edicaoAno: edicaoAno,
    edicaoNum: edicaoNum,
    phase: phase,
    faseId: fase ? fase.id : null,
    category: tipoNome || "Questão",
    historicYear: year,
    period: periodNames.map(periodoLabel).join(", "),
    periodNames: periodNames,
    tags: tagNames,
    docTipos: docTipos,
    docNomes: docNomes,
    itens: itens,
    author: docNomes.length ? docNomes[0] : "Acervo ONHB",
    date: date,
    type: docTipos.join(", ") || "Fonte histórica",
    origin: docNomes.join("; ") || "Acervo ONHB",
    language: "Português",
    img: "https://picsum.photos/seed/leiah" + q.id + "/600/400",
    searchText: searchText
  };
});

/* ================= Estado ================= */

var currentSelectedId = QUESTIONS_DATA.length ? QUESTIONS_DATA[0].id : null;
var currentPage = 1;
var itemsPerPage = 6;

var filterState = {
  searchQuery: "",
  fase: "all",
  periodo: "all",
  edicao: "all",
  yearStart: null,
  yearEnd: null,
  tags: [],
  sort: "relevant"
};

function encontrarQuestao(id) {
  return QUESTIONS_DATA.find(function (q) { return q.id === id; });
}

/* ================= Popular filtros dinamicamente ================= */

function montarOpcoes(menu, itens, rotuloTodos) {
  if (!menu) return;
  var html = '<div class="custom-option selected" data-value="all">' +
    esc(rotuloTodos) + "</div>";
  itens.forEach(function (o) {
    html += '<div class="custom-option" data-value="' + esc(o.value) + '">' +
      esc(o.label) + "</div>";
  });
  menu.innerHTML = html;
}

function popularFiltros() {
  var fasesMap = new Map();
  (D.fases || []).forEach(function (f) {
    var label = faseLabel(f);
    if (!fasesMap.has(label)) {
      fasesMap.set(label, { value: label, label: label, num: f.num });
    }
  });
  var fases = Array.from(fasesMap.values()).sort(function (a, b) {
    return a.num - b.num || a.label.localeCompare(b.label);
  });
  montarOpcoes(document.querySelector("#wrapperFase .custom-options-menu"), fases, "Todas as fases");

  var perMap = new Map();
  (D.periodos || []).forEach(function (p) {
    if (p.nome && !perMap.has(p.nome)) {
      perMap.set(p.nome, { value: p.nome, label: periodoLabel(p.nome) });
    }
  });
  montarOpcoes(document.querySelector("#wrapperPeriodo .custom-options-menu"),
    Array.from(perMap.values()), "Todos os períodos");

  var eds = (D.edicoes || []).slice()
    .sort(function (a, b) { return b.ano - a.ano; })
    .map(function (e) { return { value: String(e.ano), label: e.ano + " (" + e.num + "ª Edição)" }; });
  montarOpcoes(document.querySelector("#wrapperEdicao .custom-options-menu"), eds, "Todas as edições");

  var cont = document.getElementById("tagsFilterContainer");
  if (cont) {
    var tags = unico((D.tags || []).map(function (t) { return t.nome; }))
      .sort(function (a, b) { return a.localeCompare(b, "pt"); });
    cont.innerHTML = tags.map(function (t, i) {
      var id = "tagFiltro" + i;
      return '<div><input type="checkbox" id="' + id +
        '" class="hidden filter-tag-checkbox" value="' + esc(t) + '">' +
        '<label for="' + id + '" class="flex items-center gap-1.5 px-2.5 py-2 rounded-lg border border-gray-700 text-gray-200 bg-[#181916] cursor-pointer font-medium transition-all hover:bg-gray-700 select-none text-xs">' +
        '<i class="fa-solid fa-check text-[10px] hidden"></i> ' + esc(t) + "</label></div>";
    }).join("");

    cont.addEventListener("change", function (e) {
      var cb = e.target;
      if (!cb.classList || !cb.classList.contains("filter-tag-checkbox")) return;
      var icon = cb.nextElementSibling && cb.nextElementSibling.querySelector("i");
      if (!icon) return;
      if (cb.checked) icon.classList.remove("hidden");
      else icon.classList.add("hidden");
    });
  }
}

/* ================= Dropdowns animados (do layout) ================= */

function setupCustomAnimatedDropdowns() {
  var wrappers = document.querySelectorAll(".custom-select-wrapper");

  wrappers.forEach(function (wrapper) {
    var trigger = wrapper.querySelector(".custom-select-trigger");
    var selectedText = trigger.querySelector(".selected-text");
    if (!selectedText) return;

    trigger.addEventListener("click", function (e) {
      e.stopPropagation();
      wrappers.forEach(function (w) { if (w !== wrapper) w.classList.remove("open"); });
      wrapper.classList.toggle("open");
    });

    var options = wrapper.querySelectorAll(".custom-option");
    options.forEach(function (opt) {
      opt.addEventListener("click", function (e) {
        e.stopPropagation();
        options.forEach(function (o) { o.classList.remove("selected"); });
        opt.classList.add("selected");

        var val = opt.getAttribute("data-value");
        trigger.setAttribute("data-value", val);
        selectedText.textContent = opt.textContent.trim();
        wrapper.classList.remove("open");

        if (wrapper.id === "wrapperFase") filterState.fase = val;
        if (wrapper.id === "wrapperPeriodo") filterState.periodo = val;
        if (wrapper.id === "wrapperEdicao") filterState.edicao = val;
        if (wrapper.id === "wrapperSort") {
          filterState.sort = val;
          applyFiltersAndRender();
        }
      });
    });
  });

  document.addEventListener("click", function () {
    wrappers.forEach(function (w) { w.classList.remove("open"); });
  });
}

function resetCustomDropdowns() {
  document.querySelectorAll(".custom-select-wrapper").forEach(function (wrapper) {
    var firstOpt = wrapper.querySelector(".custom-option");
    if (!firstOpt) return;
    wrapper.querySelectorAll(".custom-option").forEach(function (o) { o.classList.remove("selected"); });
    firstOpt.classList.add("selected");
    var trigger = wrapper.querySelector(".custom-select-trigger");
    var selectedText = trigger.querySelector(".selected-text");
    trigger.setAttribute("data-value", firstOpt.getAttribute("data-value"));
    selectedText.textContent = firstOpt.textContent.trim();
  });
}

/* ================= Inicializacao ================= */

document.addEventListener("DOMContentLoaded", function () {
  popularFiltros();
  setupCustomAnimatedDropdowns();

  var scrollObserver = new IntersectionObserver(function (entries, observer) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("active");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });
  document.querySelectorAll(".reveal").forEach(function (el) { scrollObserver.observe(el); });

  var searchWrapper = document.getElementById("searchWrapper");
  var searchInput = document.getElementById("mainSearchInput");
  var searchIconBtn = document.getElementById("searchIconBtn");
  var searchCloseBtn = document.getElementById("searchCloseBtn");
  var quickSearchBtn = document.getElementById("quickSearchBtn");

  function closeSearch() {
    searchWrapper.classList.remove("active");
    searchInput.value = "";
    filterState.searchQuery = "";
    applyFiltersAndRender();
  }

  searchIconBtn && searchIconBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    if (!searchWrapper.classList.contains("active")) {
      searchWrapper.classList.add("active");
      setTimeout(function () { searchInput.focus(); }, 250);
      searchWrapper.scrollIntoView({ behavior: "smooth", block: "center" });
    } else {
      filterState.searchQuery = searchInput.value.trim().toLowerCase();
      currentPage = 1;
      applyFiltersAndRender();
    }
  });

  searchCloseBtn && searchCloseBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    closeSearch();
  });

  searchInput && searchInput.addEventListener("keyup", function (e) {
    if (e.key === "Enter") {
      filterState.searchQuery = searchInput.value.trim().toLowerCase();
      currentPage = 1;
      applyFiltersAndRender();
    }
  });

  quickSearchBtn && quickSearchBtn.addEventListener("click", function () {
    searchWrapper.classList.add("active");
    searchWrapper.scrollIntoView({ behavior: "smooth", block: "center" });
    setTimeout(function () { searchInput.focus(); }, 300);
  });

  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      searchWrapper.classList.add("active");
      searchWrapper.scrollIntoView({ behavior: "smooth", block: "center" });
      setTimeout(function () { searchInput.focus(); }, 300);
    }
  });

  document.getElementById("btnApplyFilters").addEventListener("click", function () {
    var yStart = parseInt(document.getElementById("yearStart").value, 10);
    var yEnd = parseInt(document.getElementById("yearEnd").value, 10);
    filterState.yearStart = isNaN(yStart) ? null : yStart;
    filterState.yearEnd = isNaN(yEnd) ? null : yEnd;
    filterState.tags = Array.from(document.querySelectorAll(".filter-tag-checkbox:checked"))
      .map(function (cb) { return cb.value; });
    currentPage = 1;
    applyFiltersAndRender();
    showNotification("Filtros aplicados com sucesso!");
  });

  document.getElementById("btnResetFilters").addEventListener("click", function () {
    resetCustomDropdowns();
    document.getElementById("yearStart").value = "";
    document.getElementById("yearEnd").value = "";
    document.querySelectorAll(".filter-tag-checkbox").forEach(function (cb) {
      cb.checked = false;
      var icon = cb.nextElementSibling && cb.nextElementSibling.querySelector("i");
      icon && icon.classList.add("hidden");
    });
    filterState = {
      searchQuery: "", fase: "all", periodo: "all", edicao: "all",
      yearStart: null, yearEnd: null, tags: [], sort: "relevant"
    };
    if (searchWrapper.classList.contains("active")) {
      closeSearch();
    } else {
      currentPage = 1;
      applyFiltersAndRender();
    }
    showNotification("Filtros redefinidos!");
  });

  document.getElementById("metaActionBtn").addEventListener("click", function () {
    openQuestionModal(currentSelectedId);
  });

  applyFiltersAndRender();
});

/* ================= Filtragem e render ================= */

function applyFiltersAndRender() {
  var f = filterState;
  var filtered = QUESTIONS_DATA.filter(function (q) {
    if (f.searchQuery && q.searchText.indexOf(f.searchQuery) === -1) return false;
    if (f.fase !== "all" && q.phase !== f.fase) return false;
    if (f.periodo !== "all" && q.periodNames.indexOf(f.periodo) === -1) return false;
    if (f.edicao !== "all" && String(q.edicaoAno) !== String(f.edicao)) return false;
    if (f.yearStart != null && q.historicYear != null && q.historicYear < f.yearStart) return false;
    if (f.yearEnd != null && q.historicYear != null && q.historicYear > f.yearEnd) return false;
    if (f.tags.length > 0) {
      var achou = f.tags.some(function (t) { return q.tags.indexOf(t) !== -1; });
      if (!achou) return false;
    }
    return true;
  });

  if (f.sort === "recent") {
    filtered.sort(function (a, b) { return (b.edicaoAno || 0) - (a.edicaoAno || 0); });
  } else if (f.sort === "yearAsc") {
    filtered.sort(function (a, b) { return (a.historicYear || 999999) - (b.historicYear || 999999); });
  } else if (f.sort === "yearDesc") {
    filtered.sort(function (a, b) { return (b.historicYear || 0) - (a.historicYear || 0); });
  }

  updateActiveFilterPills();

  document.getElementById("totalQuestionsCount").textContent =
    "Exibindo " + filtered.length + " de " + QUESTIONS_DATA.length + " questões cadastradas";

  var totalPages = Math.ceil(filtered.length / itemsPerPage) || 1;
  if (currentPage > totalPages) currentPage = totalPages;

  var startIndex = (currentPage - 1) * itemsPerPage;
  var paginatedItems = filtered.slice(startIndex, startIndex + itemsPerPage);

  renderQuestionCards(paginatedItems);
  renderPagination(totalPages);

  if (paginatedItems.length > 0) {
    var aindaVisivel = paginatedItems.find(function (q) { return q.id === currentSelectedId; });
    selectQuestion(aindaVisivel ? currentSelectedId : paginatedItems[0].id);
  } else {
    currentSelectedId = null;
  }
}

function renderQuestionCards(items) {
  var container = document.getElementById("questionsList");
  if (!container) return;

  if (items.length === 0) {
    container.innerHTML =
      '<div class="panel-card-custom p-8 text-center space-y-3">' +
      '<i class="fa-solid fa-folder-open text-3xl text-gray-500"></i>' +
      '<h3 class="text-base font-semibold text-gray-200">Nenhuma questão encontrada</h3>' +
      '<p class="text-xs text-gray-400">Tente ajustar os termos da busca ou remover alguns filtros laterais.</p>' +
      "</div>";
    return;
  }

  var themeStyles = ["blue", "green", "red"];
  var themeIcons = [
    "fa-solid fa-book-open", "fa-solid fa-scroll", "fa-solid fa-landmark",
    "fa-solid fa-feather-pointed", "fa-solid fa-box-archive"
  ];

  container.innerHTML = items.map(function (q, idx) {
    var isSelected = q.id === currentSelectedId ? "active-selected" : "";
    var theme = themeStyles[idx % themeStyles.length];
    var iconClass = themeIcons[idx % themeIcons.length];
    var tagsHTML = q.tags.slice(0, 4).map(function (t) {
      return '<span class="bg-black/30 text-gray-200 text-[10px] font-semibold px-2 py-0.5 rounded border border-white/10 mr-1">' +
        esc(t) + "</span>";
    }).join("");

    return '<article class="card-custom ' + theme + " " + isSelected +
      '" onclick="selectQuestion(' + q.id + ')" data-id="' + q.id + '">' +
      '<div class="card-header">' +
      '<span class="text-[10px] font-bold text-gray-200 uppercase bg-black/40 px-2.5 py-1 rounded border border-white/10 backdrop-blur-sm">' +
      "ONHB · " + esc(q.edicaoAno || "—") + " · " + esc(q.phase) + "</span>" +
      '<span class="text-[11px] text-gray-300 font-medium">' +
      '<i class="fa-regular fa-clock mr-1"></i> ' + esc(q.category) + "</span>" +
      "</div>" +
      '<div class="card-body">' +
      '<div class="icon"><i class="' + iconClass + '"></i></div>' +
      "<div>" +
      "<h3>" + esc(q.headline) + "</h3>" +
      "<p>" + esc(q.descShort) + "</p>" +
      '<div class="progress"><div>' +
      "<span>" + esc(q.period || "Período não informado") +
      (q.historicYear ? " · " + q.historicYear : "") + "</span>" +
      '<div class="progress-bar"></div></div></div>' +
      '<div class="flex flex-wrap items-center justify-between gap-2 mt-4 pt-2 border-t border-white/10">' +
      '<div class="flex flex-wrap items-center gap-1">' + tagsHTML + "</div>" +
      "<div>" +
      '<a href="javascript:void(0)" onclick="event.stopPropagation(); openQuestionModal(' + q.id + ')" class="btn-first">' +
      'Ver completa <i class="fa-solid fa-arrow-right text-[10px] ml-1"></i></a>' +
      '<a href="javascript:void(0)" onclick="event.stopPropagation(); selectQuestion(' + q.id + ')" class="btn-second">Inspetor</a>' +
      "</div></div></div></div></article>";
  }).join("");
}

function selectQuestion(id) {
  currentSelectedId = id;
  var q = encontrarQuestao(id);
  if (!q) return;

  document.querySelectorAll(".card-custom").forEach(function (card) {
    if (parseInt(card.getAttribute("data-id"), 10) === id) card.classList.add("active-selected");
    else card.classList.remove("active-selected");
  });

  var metaImg = document.getElementById("metaImage");
  metaImg.style.opacity = "0";
  setTimeout(function () {
    metaImg.src = q.img;
    metaImg.style.opacity = "1";
  }, 150);

  document.getElementById("metaTitle").textContent = q.title || "--";
  document.getElementById("metaAuthor").textContent = q.author;
  document.getElementById("metaDate").textContent = q.date;
  document.getElementById("metaType").textContent = q.type;
  document.getElementById("metaPeriod").textContent = q.period || "--";
  document.getElementById("metaOrigin").textContent = q.origin;
  document.getElementById("metaLang").textContent = q.language;
  document.getElementById("metaEditionBadge").textContent = "ONHB " + (q.edicaoAno || "");

  var tagsContainer = document.getElementById("metaTagsContainer");
  tagsContainer.innerHTML = q.tags.length
    ? q.tags.map(function (t) {
        return '<span class="bg-teal-950 text-teal-300 border border-teal-700/50 px-2 py-0.5 rounded text-[10px] font-semibold">' +
          esc(t) + "</span>";
      }).join("")
    : '<span class="text-gray-500 text-[10px] italic">Sem tags</span>';
}

function renderPagination(totalPages) {
  var pContainer = document.getElementById("paginationBar");
  if (!pContainer) return;
  if (totalPages <= 1) { pContainer.innerHTML = ""; return; }

  function janela() {
    var paginas = [];
    var inicio = Math.max(1, currentPage - 2);
    var fim = Math.min(totalPages, inicio + 4);
    inicio = Math.max(1, fim - 4);
    for (var i = inicio; i <= fim; i++) paginas.push(i);
    return paginas;
  }

  var buttons = [];
  buttons.push('<button onclick="changePage(' + (currentPage - 1) + ')" ' +
    (currentPage === 1 ? "disabled" : "") +
    ' class="w-8 h-8 rounded-lg border border-gray-600 bg-[#181916] hover:bg-gray-700 text-gray-300 flex items-center justify-center transition-colors shadow-sm disabled:opacity-40 cursor-pointer"><i class="fa-solid fa-chevron-left text-[10px]"></i></button>');

  janela().forEach(function (i) {
    var active = i === currentPage
      ? "bg-[#134e5e] text-white font-bold"
      : "border border-gray-600 bg-[#181916] hover:bg-gray-700 text-gray-300";
    buttons.push('<button onclick="changePage(' + i + ')" class="w-8 h-8 rounded-lg ' +
      active + ' flex items-center justify-center shadow-sm cursor-pointer text-xs">' + i + "</button>");
  });

  buttons.push('<button onclick="changePage(' + (currentPage + 1) + ')" ' +
    (currentPage === totalPages ? "disabled" : "") +
    ' class="w-8 h-8 rounded-lg border border-gray-600 bg-[#181916] hover:bg-gray-700 text-gray-300 flex items-center justify-center transition-colors shadow-sm disabled:opacity-40 cursor-pointer"><i class="fa-solid fa-chevron-right text-[10px]"></i></button>');

  pContainer.innerHTML = buttons.join("");
}

function changePage(page) {
  if (page < 1) return;
  currentPage = page;
  applyFiltersAndRender();
  document.getElementById("repositorio").scrollIntoView({ behavior: "smooth" });
}

function updateActiveFilterPills() {
  var container = document.getElementById("activePillsContainer");
  var badge = document.getElementById("activeFiltersBadge");
  if (!container) return;

  var pills = [];
  if (filterState.searchQuery) pills.push('Busca: "' + filterState.searchQuery + '"');
  if (filterState.fase !== "all") pills.push(filterState.fase);
  if (filterState.periodo !== "all") pills.push(periodoLabel(filterState.periodo));
  if (filterState.edicao !== "all") pills.push("ONHB " + filterState.edicao);
  if (filterState.yearStart || filterState.yearEnd) {
    pills.push((filterState.yearStart || 1500) + " - " + (filterState.yearEnd || 2026));
  }
  filterState.tags.forEach(function (t) { pills.push(t); });

  if (badge) badge.textContent = pills.length + " ativos";

  if (pills.length === 0) {
    container.innerHTML =
      '<span class="text-gray-400 text-[11px] font-medium mr-1">Filtros aplicados:</span> ' +
      '<span class="text-gray-500 text-[11px] italic">Nenhum filtro ativo no momento</span>';
  } else {
    var pillsHTML = pills.map(function (p) {
      return '<span class="inline-flex items-center gap-1 bg-teal-950 text-teal-200 font-medium px-2 py-0.5 rounded border border-teal-700/50 text-[11px]">' +
        esc(p) + "</span>";
    }).join("");
    container.innerHTML =
      '<span class="text-gray-400 text-[11px] font-medium mr-1">Filtros aplicados:</span> ' + pillsHTML;
  }
}

/* ================= Modal ================= */

function openQuestionModal(id) {
  var q = encontrarQuestao(id);
  if (!q) return;

  document.getElementById("modalEdition").textContent = "ONHB · " + q.edition + " · " + q.phase;
  document.getElementById("modalHeadline").textContent = q.headline;
  document.getElementById("modalSourceTitle").textContent =
    q.docNomes.length ? q.docNomes.join("; ") : q.type;
  document.getElementById("modalDesc").textContent = q.desc;
  document.getElementById("modalAuthor").textContent = q.author;
  document.getElementById("modalDate").textContent = q.date;
  document.getElementById("modalType").textContent = q.type;
  document.getElementById("modalOrigin").textContent = q.origin;
  document.getElementById("modalImg").src = q.img;

  var wrap = document.getElementById("modalAlternativesWrapper");
  var alt = document.getElementById("modalAlternatives");
  if (wrap && alt) {
    if (q.itens.length) {
      wrap.classList.remove("hidden");
      alt.innerHTML = q.itens.map(function (it) {
        return '<div class="bg-[#161714] p-3 rounded-lg border border-gray-800">' +
          '<div class="flex justify-between text-[11px] text-teal-300 font-semibold mb-1">' +
          "<span>" + esc(it.identificador || "Item") + "</span>" +
          "<span>" + esc(it.pontuacao) + " pontos</span></div>" +
          '<p class="text-gray-300 text-xs leading-relaxed">' + esc(it.texto || "") + "</p></div>";
      }).join("");
    } else {
      wrap.classList.add("hidden");
      alt.innerHTML = "";
    }
  }

  document.getElementById("questionModal").classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

function closeQuestionModal() {
  document.getElementById("questionModal").classList.add("hidden");
  document.body.style.overflow = "";
}

function downloadTranscription() {
  var q = encontrarQuestao(currentSelectedId);
  if (!q) return;
  var linhas = [
    "ONHB - " + q.edition + " - " + q.phase,
    "Questão " + q.num + " (" + q.category + ")",
    "Período: " + (q.period || "não informado"),
    "Datação: " + q.date,
    "Tipo: " + q.type,
    "Acervo: " + q.origin,
    "Tags: " + (q.tags.join(", ") || "nenhuma"),
    "",
    "ENUNCIADO:",
    q.desc,
    ""
  ];
  if (q.itens.length) {
    linhas.push("ALTERNATIVAS / ITENS:");
    q.itens.forEach(function (it) {
      linhas.push("[" + (it.identificador || "") + "] (" + it.pontuacao + " pts) " + (it.texto || ""));
    });
  } else {
    linhas.push("Nenhuma alternativa cadastrada.");
  }

  var blob = new Blob([linhas.join("\n")], { type: "text/plain;charset=utf-8" });
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = "questao-" + q.num + "-onhb.txt";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showNotification("Transcrição da questão baixada!");
}

function showNotification(msg) {
  var toast = document.getElementById("toastNotification");
  var toastMsg = document.getElementById("toastMsg");
  if (!toast || !toastMsg) return;
  toastMsg.textContent = msg;
  toast.classList.remove("hidden");
  toast.classList.add("flex");
  setTimeout(function () {
    toast.classList.add("hidden");
    toast.classList.remove("flex");
  }, 3200);
}
