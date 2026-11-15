/* Fills the page from content.js and handles the language buttons.
   Nothing here needs editing to change the website's text. */
(function () {
  var S = window.SITE;
  var STORAGE_KEY = "lang";
  // Only languages that actually have a text block are offered.
  var languages = S.languages.filter(function (l) { return S.text[l.code]; });
  var codes = languages.map(function (l) { return l.code; });
  // The first language (English) is the baseline: any missing text falls back to it.
  var base = S.text[codes[0]];

  function missing(v) {
    return v === undefined || v === null || v === "" || (Array.isArray(v) && v.length === 0);
  }
  function get(t, key) { return missing(t[key]) ? base[key] : t[key]; }
  function getItem(t, key, i, field) {
    var item = (t[key] || [])[i];
    var v = item && (field ? item[field] : item);
    if (missing(v)) {
      var b = base[key][i];
      v = field ? b[field] : b;
    }
    return v;
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function fill(s) {
    return String(s)
      .replace(/\{phone\}/g, S.phone.display)
      .replace(/\{year\}/g, new Date().getFullYear());
  }
  function rich(s) { return esc(fill(s)).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>"); }
  function $all(sel) { return document.querySelectorAll(sel); }

  function initialLang() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved && codes.indexOf(saved) !== -1) return saved;
    } catch (e) {}
    var prefs = navigator.languages || [navigator.language || "en"];
    for (var i = 0; i < prefs.length; i++) {
      var p = String(prefs[i]).slice(0, 2).toLowerCase();
      if (codes.indexOf(p) !== -1) return p;
    }
    return codes[0];
  }

  function render(lang) {
    var t = S.text[lang];
    document.documentElement.lang = lang;
    document.title = get(t, "metaTitle");
    var meta = document.querySelector('meta[name="description"]');
    if (meta) meta.setAttribute("content", get(t, "metaDescription"));

    $all("[data-t]").forEach(function (el) { el.textContent = fill(get(t, el.dataset.t)); });
    $all("[data-t-rich]").forEach(function (el) { el.innerHTML = rich(get(t, el.dataset.tRich)); });

    $all("[data-tel]").forEach(function (el) { el.setAttribute("href", "tel:" + S.phone.tel); });

    $all("[data-list]").forEach(function (el) {
      var key = el.dataset.list;
      // Item count comes from the baseline, so a short or missing list still shows every item.
      el.innerHTML = base[key].map(function (_, i) {
        if (key === "services") {
          return '<article class="card"><h3>' + esc(getItem(t, key, i, "title")) +
            "</h3><p>" + esc(getItem(t, key, i, "text")) + "</p></article>";
        }
        return "<li>" + esc(getItem(t, key, i)) + "</li>";
      }).join("");
    });

    $all(".lang-btn").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.lang === lang));
    });
  }

  function setLang(lang) {
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
    render(lang);
  }

  var box = document.getElementById("lang-switch");
  box.innerHTML = languages.map(function (l) {
    return '<button type="button" class="lang-btn" data-lang="' + l.code + '" lang="' + l.code +
      '" title="' + esc(l.name) + '" aria-label="' + esc(l.name) + '">' + esc(l.label) + "</button>";
  }).join("");
  box.addEventListener("click", function (e) {
    var b = e.target.closest(".lang-btn");
    if (b) setLang(b.dataset.lang);
  });

  render(initialLang());
})();
