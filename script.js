/* Fills the page from content.js and handles the language picker.
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

    var current = languages.filter(function (l) { return l.code === lang; })[0];
    var toggle = document.querySelector(".lang-toggle");
    toggle.querySelector(".lang-code").textContent = current.label;
    toggle.setAttribute("aria-label", current.name);
    $all(".lang-item").forEach(function (b) {
      if (b.dataset.lang === lang) b.setAttribute("aria-current", "true");
      else b.removeAttribute("aria-current");
    });
  }

  function setLang(lang) {
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
    render(lang);
  }

  // Language picker: a globe icon beside a button that opens a small menu of languages.
  var GLOBE = '<svg class="lang-globe" aria-hidden="true" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.5 2.4 3.8 5.4 3.8 9s-1.3 6.6-3.8 9c-2.5-2.4-3.8-5.4-3.8-9S9.5 5.4 12 3z"/></svg>';
  var CARET = '<svg class="lang-caret" aria-hidden="true" viewBox="0 0 12 12" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4.5l4 4 4-4"/></svg>';

  var box = document.getElementById("lang-switch");
  box.innerHTML = GLOBE +
    '<div class="lang-picker">' +
      '<button type="button" class="lang-toggle" aria-haspopup="true" aria-expanded="false" aria-controls="lang-menu">' +
        '<span class="lang-code"></span>' + CARET + "</button>" +
      '<div class="lang-menu" id="lang-menu" hidden>' +
        languages.map(function (l) {
          return '<button type="button" class="lang-item" data-lang="' + l.code + '" lang="' + l.code + '">' +
            esc(l.name) + "</button>";
        }).join("") +
      "</div>" +
    "</div>";

  var toggle = box.querySelector(".lang-toggle");
  var menu = box.querySelector(".lang-menu");

  function setOpen(open, refocus) {
    menu.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    if (!open && refocus) toggle.focus();
  }

  toggle.addEventListener("click", function () { setOpen(menu.hidden); });
  menu.addEventListener("click", function (e) {
    var b = e.target.closest(".lang-item");
    if (!b) return;
    setLang(b.dataset.lang);
    setOpen(false, true);
  });
  document.addEventListener("click", function (e) {
    if (!box.contains(e.target)) setOpen(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !menu.hidden) setOpen(false, true);
  });

  render(initialLang());
})();
