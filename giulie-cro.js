/* ===================================================================
 * Altiva · Giulié (The Hood) — Script CRO de tienda
 * -------------------------------------------------------------------
 * Rollout incremental. Kill-switch = desregistrar vía Scripts API
 *   (python tn_scripts.py del <id>).  No reemplaza el botón de compra.
 *
 * Features activos en este build:
 *   #6  Sticky CTA móvil (solo PDP, solo ≤768px)
 *   #8  Bloque de confianza + línea de garantía (solo PDP, junto al CTA)
 *
 * Anclas estables del theme (verificadas en el DOM 2026-06-15):
 *   .js-addtocart  ·  #price_display / .js-price-display
 *
 * Copy: textos confirmados por Giulié (copy-tienda-giulie.md, 2026-06-13).
 * =================================================================== */
(function () {
  "use strict";

  var NS = "__altivaGiulie";
  if (window[NS] && window[NS].loaded) return;          // idempotencia
  window[NS] = { loaded: true, version: "2026-06-15.1" };

  /* ---------- helpers ---------- */
  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }
  // Espera a un selector que puede renderizar tarde (tienda JS-heavy)
  function waitFor(sel, cb, tries) {
    tries = (tries == null) ? 40 : tries;               // ~6s máx
    var el = document.querySelector(sel);
    if (el) return cb(el);
    if (tries <= 0) return;
    setTimeout(function () { waitFor(sel, cb, tries - 1); }, 150);
  }
  function isPDP() {
    return !!document.querySelector('[data-component="product.add-to-cart"], .js-addtocart');
  }

  /* ---------- estilos ---------- */
  function injectCSS() {
    if (document.getElementById("ag-css")) return;
    var s = document.createElement("style");
    s.id = "ag-css";
    s.textContent =
      /* --- sticky CTA móvil --- */
      ".ag-sticky{position:fixed;left:0;right:0;bottom:0;z-index:9990;display:none;" +
      "align-items:center;justify-content:space-between;gap:12px;" +
      "padding:10px 14px;background:#fff;border-top:1px solid #e7e3dd;" +
      "box-shadow:0 -6px 18px rgba(0,0,0,.08);font-family:inherit}" +
      ".ag-sticky__price{font-weight:700;font-size:1.05rem;line-height:1.1;color:#1a1a1a;white-space:nowrap}" +
      ".ag-sticky__btn{flex:1 1 auto;max-width:62%;border:0;border-radius:8px;padding:13px 16px;" +
      "font-size:1rem;font-weight:700;cursor:pointer;background:#1a1a1a;color:#fff;" +
      "-webkit-appearance:none;appearance:none}" +
      ".ag-sticky__btn:active{opacity:.85}" +
      "@media(max-width:768px){.ag-sticky.is-visible{display:flex}body.ag-has-sticky{padding-bottom:68px}}" +
      /* --- bloque de confianza --- */
      ".ag-trust{margin:14px 0 4px;padding:12px 0;border-top:1px solid #eceae5;border-bottom:1px solid #eceae5;" +
      "display:grid;grid-template-columns:1fr 1fr;gap:10px 14px}" +
      ".ag-trust__i{display:flex;align-items:flex-start;gap:8px;font-size:.82rem;line-height:1.25;color:#3a3a3a}" +
      ".ag-trust__i b{font-weight:600;color:#1a1a1a}" +
      ".ag-trust__ico{font-size:1rem;line-height:1.1;flex:0 0 auto}" +
      ".ag-guarantee{margin:10px 0 2px;font-size:.82rem;line-height:1.3;color:#5a5147}" +
      "@media(min-width:769px){.ag-trust{grid-template-columns:1fr 1fr 1fr 1fr}}";
    document.head.appendChild(s);
  }

  /* ---------- #6 Sticky CTA móvil (PDP) ---------- */
  function stickyCTA(realBtn) {
    if (document.querySelector(".ag-sticky")) return;

    var priceEl = document.querySelector("#price_display, .js-price-display");
    var bar = document.createElement("div");
    bar.className = "ag-sticky";
    bar.innerHTML =
      '<span class="ag-sticky__price"></span>' +
      '<button type="button" class="ag-sticky__btn">Lo quiero</button>';
    document.body.appendChild(bar);
    document.body.classList.add("ag-has-sticky");

    var priceOut = bar.querySelector(".ag-sticky__price");
    function syncPrice() { if (priceEl) priceOut.textContent = priceEl.textContent.trim(); }
    syncPrice();
    // Re-sincroniza el precio cuando cambia la variante
    if (priceEl) new MutationObserver(syncPrice).observe(priceEl, { childList: true, characterData: true, subtree: true });

    // El sticky NUNCA reemplaza la lógica de compra: dispara el botón real
    bar.querySelector(".ag-sticky__btn").addEventListener("click", function () {
      realBtn.click();
    });

    // Mostrar solo cuando el botón real queda fuera de pantalla
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        bar.classList.toggle("is-visible", !entries[0].isIntersecting);
      }, { threshold: 0 }).observe(realBtn);
    } else {
      bar.classList.add("is-visible");
    }
  }

  /* ---------- #8 Bloque de confianza + garantía (PDP) ---------- */
  function trustBlock(realBtn) {
    if (document.querySelector(".ag-trust")) return;

    var anchor = realBtn.closest("form") || realBtn.parentElement;
    if (!anchor) return;

    var ITEMS = [
      ["🚚", "Envío a todo el país", "Despacho en 48 h, entrega en hasta 10 días hábiles."],
      ["🔁", "Cambios dentro de 30 días", "Por rotura o daño, el envío del cambio lo pagamos nosotros."],
      ["🤎", "Garantía de 7 días", "Si no cumplió tus expectativas, te devolvemos el dinero."],
      ["💳", "Pagá como quieras", "6 cuotas sin interés · 20% OFF con transferencia."]
    ];
    var grid = '<div class="ag-trust">';
    for (var i = 0; i < ITEMS.length; i++) {
      grid += '<div class="ag-trust__i"><span class="ag-trust__ico">' + ITEMS[i][0] + '</span>' +
        '<span><b>' + ITEMS[i][1] + '</b><br>' + ITEMS[i][2] + '</span></div>';
    }
    grid += '</div>';

    var wrap = document.createElement("div");
    wrap.setAttribute("data-altiva-cro", "trust");
    wrap.innerHTML = grid +
      '<p class="ag-guarantee">Garantía de 7 días 🤎 — Confiamos en nuestros productos; ' +
      'si no cumplió tus expectativas, te devolvemos el dinero.</p>';
    anchor.parentNode.insertBefore(wrap, anchor.nextSibling);
  }

  /* ---------- init ---------- */
  ready(function () {
    if (!isPDP()) return;                 // de momento, features solo en PDP
    injectCSS();
    waitFor(".js-addtocart", function (btn) {
      // Si el producto está sin stock, el theme oculta/deshabilita el botón: respetamos eso
      try { stickyCTA(btn); } catch (e) {}
      try { trustBlock(btn); } catch (e) {}
    });
  });
})();
