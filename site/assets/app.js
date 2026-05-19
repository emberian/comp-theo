/* Shared site JS: nav, a tiny markdown renderer, gallery + modal. No deps. */
(function () {
  "use strict";
  var PAGES = [
    ["index.html", "Overview"],
    ["gallery.html", "Poster Browser"],
    ["essays/index.html", "Essays"],
    ["lessons/index.html", "Lessons"],
    ["compare/index.html", "Comparisons"],
    ["glossary.html", "Glossary"],
    ["map.html", "Poster Map"],
  ];

  // Path back to site root from the current page depth.
  var ROOT = (location.pathname.replace(/\/+$/, "").split("/").length >
    (location.pathname.indexOf("/essays/") + 1 ||
     location.pathname.indexOf("/lessons/") + 1 ||
     location.pathname.indexOf("/compare/") + 1 ? 0 : 0)) ? "" : "";
  // Simpler & robust: depth from a data attribute on <body>.
  ROOT = document.body.getAttribute("data-root") || "";

  function buildHeader() {
    var here = location.pathname.split("/").slice(-1)[0] || "index.html";
    var inSub = /\/(essays|lessons|compare)\//.test(location.pathname);
    var h = document.createElement("header");
    h.className = "site";
    var nav = '<nav><a class="brand" href="' + ROOT +
      'index.html">Computational Theology</a>';
    PAGES.forEach(function (p) {
      var href = ROOT + p[0];
      var active = (p[0].indexOf(here) > -1 &&
        (inSub ? p[0].indexOf("/") > -1 : true)) ? " class='active'" : "";
      nav += '<a' + active + ' href="' + href + '">' + p[1] + "</a>";
    });
    nav += "</nav>";
    h.innerHTML = nav;
    document.body.insertBefore(h, document.body.firstChild);
  }

  function buildFooter() {
    var f = document.createElement("footer");
    f.className = "site";
    f.innerHTML =
      "An archive & critical reading of the <em>Computational Theology</em> " +
      "poster series (210 panels, 5 parts). Transcriptions machine-generated " +
      "(codex / Claude); essays are interpretive and skeptical, not the " +
      "project's own voice. Source posters © their author.";
    document.body.appendChild(f);
  }

  /* Minimal, safe-ish markdown -> HTML (headings, lists, blockquote,
     bold/italic/code, links, hr, paragraphs). Escapes HTML first. */
  function md(src) {
    function esc(s) {
      return s.replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    }
    var lines = esc(src).replace(/\r/g, "").split("\n");
    var out = [], i = 0, list = null;
    function inline(t) {
      return t
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
        .replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
    }
    function closeList() { if (list) { out.push("</" + list + ">"); list = null; } }
    for (; i < lines.length; i++) {
      var l = lines[i], m;
      if (/^\s*$/.test(l)) { closeList(); continue; }
      if ((m = l.match(/^(#{1,4})\s+(.*)/))) {
        closeList();
        out.push("<h" + m[1].length + ">" + inline(m[2]) +
          "</h" + m[1].length + ">");
      } else if (/^---+\s*$/.test(l)) {
        closeList(); out.push("<hr>");
      } else if ((m = l.match(/^\s*[-*]\s+(.*)/))) {
        if (list !== "ul") { closeList(); out.push("<ul>"); list = "ul"; }
        out.push("<li>" + inline(m[1]) + "</li>");
      } else if ((m = l.match(/^\s*\d+\.\s+(.*)/))) {
        if (list !== "ol") { closeList(); out.push("<ol>"); list = "ol"; }
        out.push("<li>" + inline(m[1]) + "</li>");
      } else if ((m = l.match(/^>\s?(.*)/))) {
        closeList();
        out.push("<blockquote>" + inline(m[1]) + "</blockquote>");
      } else {
        closeList(); out.push("<p>" + inline(l) + "</p>");
      }
    }
    closeList();
    return out.join("\n");
  }

  function renderMarkdownInto(sel, dataFile) {
    fetch(ROOT + "data/" + dataFile).then(function (r) { return r.text(); })
      .then(function (t) {
        document.querySelector(sel).innerHTML = md(t);
      }).catch(function () {
        document.querySelector(sel).textContent =
          "Could not load " + dataFile;
      });
  }

  /* ---------- Gallery ---------- */
  function initGallery() {
    var root = document.getElementById("gallery");
    if (!root) return;
    var state = { posters: [], filter: "all", q: "", view: [] };

    fetch(ROOT + "data/posters.json")
      .then(function (r) { return r.json(); })
      .then(function (d) {
        state.posters = d.posters;
        buildToolbar(d);
        render();
      });

    function buildToolbar(d) {
      var tb = document.getElementById("toolbar");
      var btns = '<button data-f="all" class="active">All ' +
        d.posters.length + "</button>";
      d.parts.forEach(function (p) {
        btns += '<button data-f="' + p.part + '">' +
          p.part + " · " + p.count + "</button>";
      });
      tb.innerHTML = btns +
        '<input id="q" placeholder="search transcriptions…">' +
        '<span class="count" id="count"></span>';
      tb.addEventListener("click", function (e) {
        var b = e.target.closest("button[data-f]");
        if (!b) return;
        state.filter = b.getAttribute("data-f");
        [].forEach.call(tb.querySelectorAll("button"), function (x) {
          x.classList.toggle("active", x === b);
        });
        render();
      });
      document.getElementById("q").addEventListener("input", function (e) {
        state.q = e.target.value.toLowerCase();
        render();
      });
    }

    function render() {
      state.view = state.posters.filter(function (p) {
        if (state.filter !== "all" && p.part !== state.filter) return false;
        if (state.q) {
          var hay = (p.title + " " + p.transcription + " " +
            p.visual).toLowerCase();
          if (hay.indexOf(state.q) < 0) return false;
        }
        return true;
      });
      document.getElementById("count").textContent =
        state.view.length + " shown";
      var g = document.createElement("div");
      g.className = "grid";
      state.view.forEach(function (p, idx) {
        var d = document.createElement("div");
        d.className = "thumb";
        d.innerHTML = '<span class="tag">' + p.part + " · " +
          ("00" + p.index).slice(-3) + '</span><img loading="lazy" alt="' +
          p.title.replace(/"/g, "&quot;") + '" data-src="' +
          ROOT + p.img + '">';
        d.addEventListener("click", function () { openModal(idx); });
        g.appendChild(d);
      });
      root.innerHTML = "";
      root.appendChild(g);
      lazy();
    }

    function lazy() {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting) return;
          var im = e.target;
          im.src = im.getAttribute("data-src");
          im.onload = function () { im.classList.add("loaded"); };
          io.unobserve(im);
        });
      }, { rootMargin: "400px" });
      [].forEach.call(root.querySelectorAll("img[data-src]"),
        function (im) { io.observe(im); });
    }

    var mi = -1;
    var modal = document.getElementById("modal");
    function openModal(i) {
      mi = i;
      var p = state.view[i];
      var codexTabs = p.codex ?
        '<div class="tabs"><button class="active" data-src="c">' +
        "Claude/codex (archive)</button>" +
        '<button data-src="x">codex re-pass</button></div>' : "";
      modal.querySelector(".inner").innerHTML =
        '<div><img src="' + ROOT + p.img + '" alt=""></div>' +
        '<div><div class="meta">' + p.part + " · panel " + p.index +
        " · id " + p.id + " · parsed by " + p.engine + "</div>" +
        "<h2>" + p.title + "</h2>" + codexTabs +
        '<div id="tx"></div></div>';
      showText(p, "c");
      if (p.codex) {
        modal.querySelectorAll(".tabs button").forEach(function (b) {
          b.addEventListener("click", function () {
            modal.querySelectorAll(".tabs button").forEach(function (x) {
              x.classList.toggle("active", x === b);
            });
            showText(p, b.getAttribute("data-src"));
          });
        });
      }
      modal.classList.add("open");
      document.body.style.overflow = "hidden";
    }
    function showText(p, which) {
      var t = (which === "x" && p.codex) ? p.codex : p;
      modal.querySelector("#tx").innerHTML =
        "<h3>Transcription</h3><pre>" +
        (t.transcription || "(none)").replace(/</g, "&lt;") +
        "</pre><h3>Visual</h3><pre>" +
        (t.visual || "(none)").replace(/</g, "&lt;") + "</pre>";
    }
    function close() {
      modal.classList.remove("open");
      document.body.style.overflow = "";
    }
    function step(d) {
      var n = mi + d;
      if (n >= 0 && n < state.view.length) openModal(n);
    }
    modal.innerHTML =
      '<button class="x" aria-label="close">×</button>' +
      '<button class="nav prev" aria-label="prev">‹</button>' +
      '<button class="nav next" aria-label="next">›</button>' +
      '<div class="inner"></div>';
    modal.querySelector(".x").onclick = close;
    modal.querySelector(".prev").onclick = function () { step(-1); };
    modal.querySelector(".next").onclick = function () { step(1); };
    modal.addEventListener("click", function (e) {
      if (e.target === modal) close();
    });
    document.addEventListener("keydown", function (e) {
      if (!modal.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") step(-1);
      if (e.key === "ArrowRight") step(1);
    });
  }

  window.CT = { md: md, renderMarkdownInto: renderMarkdownInto };
  document.addEventListener("DOMContentLoaded", function () {
    buildHeader();
    initGallery();
    buildFooter();
  });
})();
