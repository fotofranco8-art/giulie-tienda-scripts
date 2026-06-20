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
 *   #7  Cross-sell "Completá tu ritual" (refill + home spray) bajo el botón,
 *       SOLO en el PDP del difusor. v1 = cards que linkean al PDP del complemento.
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
  window[NS] = { loaded: true, version: "2026-06-20.3" };

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
      /* --- #3 Aroma legible: el select del bundle se apila a ancho completo en móvil.
         !important para ganarle al CSS de la app del bundle (que lo fija en 95px). --- */
      "@media(max-width:768px){.variant-product-row{flex-wrap:wrap!important}" +
      ".variant-product-row .select-wrap{width:100%!important;flex:1 1 100%!important;margin:0 0 6px!important}" +
      ".variant-product-row .select{width:100%!important;min-width:0!important}}" +
      /* --- #7 Cross-sell "Completá tu ritual" --- */
      ".ag-xs{margin:18px 0 4px;padding:14px 0;border-top:1px solid #eceae5}" +
      ".ag-xs__t{font-size:.95rem;font-weight:700;color:#1a1a1a;margin:0 0 10px}" +
      ".ag-xs__card{display:flex;align-items:center;gap:10px;padding:8px;border:1px solid #eceae5;" +
      "border-radius:10px;margin-bottom:8px;text-decoration:none;color:inherit;background:#fff}" +
      ".ag-xs__card:active{background:#faf9f7}" +
      ".ag-xs__img{width:56px;height:56px;object-fit:cover;border-radius:8px;flex:0 0 auto;background:#f4f2ee}" +
      ".ag-xs__info{display:flex;flex-direction:column;gap:2px;flex:1 1 auto;min-width:0}" +
      ".ag-xs__name{font-size:.86rem;font-weight:600;color:#1a1a1a;line-height:1.2}" +
      ".ag-xs__desc{font-size:.76rem;color:#6a625a;line-height:1.2}" +
      ".ag-xs__price{font-size:.86rem;font-weight:700;color:#1a1a1a}" +
      ".ag-xs__cta{flex:0 0 auto;font-size:.8rem;font-weight:700;color:#1a1a1a;white-space:nowrap;align-self:center}";
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

  /* ---------- #7 Cross-sell "Completá tu ritual" (solo PDP difusor) ---------- */
  function isDifusor() { return location.pathname.indexOf("/difusor-the-hood") >= 0; }
  function crossSell(realBtn) {
    if (document.querySelector('[data-altiva-cro="xsell"]')) return;
    var anchor = realBtn.closest("form") || realBtn.parentElement;
    if (!anchor) return;

    var ITEMS = [
      { url: "/productos/refill1/",
        img: "https://acdn-us.mitiendanube.com/stores/006/937/942/products/42-24ebef50a09a68122c17636822993962-1024-1024.png",
        name: "Refill para Difusor", desc: "Rinde 2 recargas: tu aroma dura el triple", price: "$32.500" },
      { url: "/productos/home-spray-the-hood/",
        img: "https://acdn-us.mitiendanube.com/stores/006/937/942/products/24-c92260d13a464797ad17636815187763-1024-1024.png",
        name: "Home Spray", desc: "El mismo aroma para refrescar al instante", price: "$24.500" }
    ];
    var html = '<p class="ag-xs__t">Completá tu ritual 🤎</p>';
    for (var i = 0; i < ITEMS.length; i++) {
      var it = ITEMS[i];
      html += '<a class="ag-xs__card" href="' + it.url + '">' +
        '<img class="ag-xs__img" src="' + it.img + '" alt="" loading="lazy" onerror="this.style.display=\'none\'">' +
        '<span class="ag-xs__info"><span class="ag-xs__name">' + it.name + '</span>' +
        '<span class="ag-xs__desc">' + it.desc + '</span>' +
        '<span class="ag-xs__price">' + it.price + '</span></span>' +
        '<span class="ag-xs__cta">Verlo →</span></a>';
    }
    var wrap = document.createElement("div");
    wrap.className = "ag-xs";
    wrap.setAttribute("data-altiva-cro", "xsell");
    wrap.innerHTML = html;
    anchor.parentNode.insertBefore(wrap, anchor.nextSibling);
  }

  /* ---------- init ---------- */
  ready(function () {
    try { tameCookieBanner(); } catch (e) {}   // toda la tienda
    if (!isPDP()) return;                       // el resto, solo en PDP
    injectCSS();
    waitFor(".js-addtocart", function (btn) {
      // Si el producto está sin stock, el theme oculta/deshabilita el botón: respetamos eso
      try { stickyCTA(btn); } catch (e) {}
      if (isDifusor()) { try { crossSell(btn); } catch (e) {} }
    });
  });
})();
