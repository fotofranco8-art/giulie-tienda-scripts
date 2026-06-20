/* ===================================================================
 * Altiva · Giulié (The Hood) — Script CRO de tienda
 * -------------------------------------------------------------------
 * Rollout incremental. Kill-switch = desregistrar vía Scripts API
 *   (python tn_scripts.py del <id>).  No reemplaza el botón de compra.
 *
 * Features activos en este build:
 *   #6  Sticky CTA móvil (solo PDP, solo ≤768px)
 *   #2  Cookie banner: auto-dismiss al primer scroll/tap (toda la tienda)
 *   #f  WhatsApp flotante no tapa el sticky CTA (PDP móvil)
 *   #3  Aroma legible: el select del bundle (.variant-product-row) se apila a
 *       ancho completo en móvil para mostrar el nombre entero (no "Bloo…")
 *
 * NOTA: el bloque de confianza/garantía/envío/pago lo provee la app **Wigy**
 * (en el buy-box, junto al precio). Se quitó el #8 de este script para NO duplicar.
 *
 * Anclas estables del theme (verificadas en el DOM 2026-06-15/19):
 *   .js-addtocart · #price_display/.js-price-display · .js-notification-cookie-banner
 *   .js-acknowledge-cookies · .js-btn-fixed-bottom (WhatsApp flotante)
 *
 * Copy: textos confirmados por Giulié (copy-tienda-giulie.md, 2026-06-13).
 * =================================================================== */
(function () {
  "use strict";

  var NS = "__altivaGiulie";
  if (window[NS] && window[NS].loaded) return;          // idempotencia
  window[NS] = { loaded: true, version: "2026-06-20.1" };

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
      /* --- WhatsApp flotante: que no pise el sticky CTA en móvil --- */
      "@media(max-width:768px){body.ag-has-sticky .js-btn-fixed-bottom{bottom:80px}}" +
      /* --- #3 Aroma legible: el select del bundle se apila a ancho completo en móvil --- */
      "@media(max-width:768px){.variant-product-row{flex-wrap:wrap}" +
      ".variant-product-row .select-wrap{width:100%;flex:1 1 100%;margin:0 0 6px}" +
      ".variant-product-row .select{width:100%;min-width:0}}";
    document.head.appendChild(s);
  }

  /* ---------- #2 Cookie banner: que no tape el precio/CTA ---------- */
  // El banner está fijo abajo y tapa la zona de compra en el primer render móvil.
  // Lo cerramos al primer scroll/tap usando el propio botón del theme (set-cookie,
  // no se vuelve a mostrar). No falsea consentimiento: es una notificación, no un gate.
  function tameCookieBanner() {
    var done = false;
    function dismiss() {
      if (done) return;
      var banner = document.querySelector(".js-notification-cookie-banner");
      var ack = document.querySelector(".js-acknowledge-cookies");
      if (banner && banner.offsetParent !== null && ack) {
        done = true;
        ack.click();
        window.removeEventListener("scroll", dismiss);
        window.removeEventListener("touchstart", dismiss);
      }
    }
    window.addEventListener("scroll", dismiss, { passive: true });
    window.addEventListener("touchstart", dismiss, { passive: true });
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

  /* ---------- init ---------- */
  ready(function () {
    try { tameCookieBanner(); } catch (e) {}   // toda la tienda
    if (!isPDP()) return;                       // el resto, solo en PDP
    injectCSS();
    waitFor(".js-addtocart", function (btn) {
      // Si el producto está sin stock, el theme oculta/deshabilita el botón: respetamos eso
      try { stickyCTA(btn); } catch (e) {}
    });
  });
})();
