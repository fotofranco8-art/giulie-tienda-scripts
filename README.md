# giulie-tienda-scripts

Scripts CRO de la tienda de **Giulié (The Hood)** — `giulie4.mitiendanube.com` / `www.giuliefragancias.com`.
Este repo es la **fuente de verdad** (control de versiones). El archivo desplegado se **hostea en el Portal de Partners** (app "Altiva Ads"), NO en jsDelivr.

## Archivos
- `giulie-cro.js` — script CRO (sticky CTA móvil, cross-sell, cookie dismiss, empty-cart).
  **Re-portado al theme Rio (2026-07-07)**: componentes re-estilados a terracota/2px/uppercase
  y cross-sell del difusor re-cableado POR AROMA tras el split de catálogo.
- `giulie-rio-custom.css` — **CSS custom para el theme Rio**. Reproduce 1:1 el look de
  glodcasa (grilla, cards, controles de listado, selector de variantes) con terracota
  #B25C32 como único acento. Se pega en el editor de Rio → *Personalizar tu tienda →
  (Avanzado) Código CSS*. Generado desde el DOM real de glodcasa.
- `split_aromas.py` — reestructura de catálogo: un PRODUCTO independiente por aroma en
  todas las categorías (~25 productos finales). Dry-run por defecto; `APPLY=1` crea vía API.
- `REDIRECTS.md` — lista de 301 (handles madre viejos → categoría) para cargar en el Dashboard.

## Migración estética → look glodcasa (theme Rio, 2026-07)
glodcasa.com corre sobre el theme **Rio** de Tiendanube; Giulié usa **Recife**. La migración
= cambiar Giulié a Rio (en un **preview sin publicar**) + configurar tokens en el editor +
pegar `giulie-rio-custom.css` + split de catálogo + re-port del CRO. Ver el plan completo en
`~/.claude/plans/https-glodcasa-com-quiero-migrar-la-tingly-piglet.md`.

Orden: **Fase 1** (tema Rio + CSS + CRO, reversible) → **Fase 2** (split de catálogo, con el
look ya aprobado). Preview-only hasta OK de Franco. Rollback del tema = re-publicar Recife.

## Despliegue (IMPORTANTE — leer)
La Scripts API ya **no acepta `src` externo** (da 422): el JS debe estar hosteado bajo el dominio del Partner.
El script vive en `https://apps-scripts.tiendanube.com/altiva-ads/script-cro-giulie/1.js?versionId=…`
y está asociado a la tienda con **script_id 7481** (event `onfirstinteraction`, location `store`).

Para desplegar un cambio:
1. Commit + push de este repo (versionado).
2. **Portal de Partners → app "Altiva Ads" → Scripts → `script-cro-giulie/1.js`** → pegar el contenido
   nuevo de `giulie-cro.js` y guardar. Tiendanube genera un `versionId` nuevo que propaga a la tienda.
3. Verificar en vivo: `python meta-ads-manager/tn_scripts.py list` (debe seguir habiendo **1** script, id 7481)
   y `curl` al `src` para confirmar el contenido. `tn_scripts.py del 7481` = **kill-switch** (baja inmediata).

> ⚠ NO hay flujo jsDelivr activo (el README viejo lo decía; quedó descartado por el 422). `tn_scripts.py`
> solo hace `list` / `assoc <id>` / `del <id>`: asocia/desasocia, **no sube el archivo**.

## Notas
- Rollout incremental, con Franco haciendo de ojo en cada feature (la tienda es JS-heavy, no se testea 100% headless).
- Anclas estables del theme: `.js-addtocart`, `#price_display`. No reemplaza el botón de compra real.
- Copy confirmado por Giulié (2026-06-13).
