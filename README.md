# giulie-tienda-scripts

Scripts CRO de la tienda de **Giulié (The Hood)** — `giulie4.mitiendanube.com`.
Servidos por jsDelivr y registrados en la tienda vía Tiendanube **Scripts API** (app "Altiva Ads").

## Archivos
- `giulie-cro.js` — sticky CTA móvil (PDP) + bloque de confianza + línea de garantía (PDP).

## Despliegue
1. Commit + push de este repo.
2. URL jsDelivr pineada al commit (inmutable):
   `https://cdn.jsdelivr.net/gh/fotofranco8-art/giulie-tienda-scripts@<commit>/giulie-cro.js`
3. Registrar / actualizar con `meta-ads-manager/tn_scripts.py`:
   - `python tn_scripts.py add <URL>`  → alta
   - `python tn_scripts.py list`       → ver registrados
   - `python tn_scripts.py del <id>`   → **kill-switch** (baja inmediata)

## Notas
- Rollout incremental, con Franco haciendo de ojo en cada feature (la tienda es JS-heavy, no se testea 100% headless).
- Anclas estables del theme: `.js-addtocart`, `#price_display`. No reemplaza el botón de compra real.
- Copy confirmado por Giulié (2026-06-13).
