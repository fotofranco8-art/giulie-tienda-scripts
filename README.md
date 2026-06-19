# giulie-tienda-scripts

Scripts CRO de la tienda de **Giulié (The Hood)** — `giulie4.mitiendanube.com` / `www.giuliefragancias.com`.
Este repo es la **fuente de verdad** (control de versiones). El archivo desplegado se **hostea en el Portal de Partners** (app "Altiva Ads"), NO en jsDelivr.

## Archivos
- `giulie-cro.js` — sticky CTA móvil (PDP) + bloque de confianza (PDP). Un solo archivo.

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
