# Checklist de deploy — Rio en preview (Franco, Dashboard)

Rio ya está instalado en preview (confirmado 2026-07-16). Falta lo manual — el editor
visual de Tiendanube no tiene API, así que estos 3 pasos son a mano. Todo queda en
**preview, sin publicar**, hasta que lo revises y des el OK.

## 1. Tokens de color/fuente (editor visual → Diseño → Colores/Tipografía)

| Variable Rio | Valor |
|---|---|
| `--main-background` | `#FFFAF3` |
| `--main-foreground` | `#171717` |
| `--accent-color` / `--button-background` | `#B25C32` (terracota) |
| `--button-foreground` | `#FFFFFF` |
| `--label-background` / `--label-foreground` | `#B25C32` / `#FFFAF3` |
| `--adbar` / `--header` / `--footer` bg·fg | `#FFFAF3` / `#171717` |
| `--newsletter` bg·fg | `#FFFAF3` / `#171717` |
| `--success` / `--danger` / `--warning` | dejar los default de Rio |
| `--heading-font` / `--body-font` | `Public Sans` |
| border-radius / form border | `2px` / `1px solid #000` |

**Regla de oro:** el negro `#171717` queda para texto/estructura/bordes; el terracota
`#B25C32` reemplaza TODO lo que en glodcasa es negro-botón (CTA, links, hovers, labels,
indicador activo). No mezclar: si un elemento no es texto ni borde, es terracota.

## 2. Pegar el CSS custom

*Personalizar tu tienda → (Avanzado) Código CSS* → pegar el contenido completo de
[`giulie-rio-custom.css`](./giulie-rio-custom.css) (ya en el repo, commiteado).
Reproduce 1:1 la grilla/cards/controles de listado/selector de variantes de glodcasa +
el acordeón del PDP (bloque `/* ACCORDION PRODUCT */`).

## 3. Secciones del home (editor, sección por sección)

- **Announcement bar**: marquee rotativo, 3 mensajes (`copy-tienda-giulie.md` §1).
- **Header**: logo Giulié, nav en mayúsculas, hamburger con foto de interior.
- **Hero**: usar las imágenes ya generadas con texto horneado en
  `MARKETING/GENERALISTA/CLIENTES/GIULIE/web-rio-2026-07/hero/` (desktop + mobile) —
  **no** el overlay-por-CSS, eso ya se descartó (se veía "barato").
- **Welcome / Featured / Banners**: copy en `copy-tienda-giulie.md` §2-§4.
- **Footer**: `.foot-bubble` circular en terracota + newsletter.

## 4. Deploy del script CRO (después de pegar el CSS)

1. Ya está commiteado en el repo (`giulie-cro.js`, versión `2026-07-16.1-rio`, incluye
   ahora los 2 paneles nuevos de acordeón: **Notas olfativas** + **Envío y cambios**).
2. Portal de Partners → app **"Altiva Ads"** → Scripts → `script-cro-giulie/1.js` →
   pegar el contenido nuevo de `giulie-cro.js` → guardar.
3. Deploy en el Portal hasta **Producción** (no alcanza con guardar en Borrador —
   gotcha ya vivido: si queda en Borrador, `current_version` no se puebla y el
   storefront sigue sirviendo la versión vieja).
4. Verificar: `python meta-ads-manager/tn_scripts.py list` → debe seguir habiendo
   **1 solo script**, id `7481`, con `current_version` avanzado.
5. **Ojo con el caché**: el storefront puede tardar horas en servir la versión nueva
   aunque la API ya diga que está actualizada (vivido el 20/06). No repetir el deploy
   en loop pensando que falló — la API es la fuente de verdad de que salió bien.

## 5. Verificación visual (vos, en el preview — no soy capaz de verlo desde acá)

Como el preview de Rio no es público y no tengo browser con sesión en esta corrida,
esta parte la hacés vos. Checklist puntual:

- [ ] Grilla de categoría: 3 columnas (X3), ratio 1:1 en las fotos, hover con 2ª imagen.
- [ ] Selector de variantes en PDP: pills, no dropdown feo.
- [ ] **Acordeón del PDP: 5 paneles** — Descripción / Medios de pago / Compartir
      (nativos) + **Notas olfativas** + **Envío y cambios** (nuevos, míos). Mismo
      estilo visual entre los 5 (borde, tipografía, spacing).
- [ ] Notas olfativas muestra el texto correcto según el aroma elegido en el `<select>`.
- [ ] Terracota como único acento (nada de negro en botones/CTAs).
- [ ] Sticky CTA móvil + cross-sell "Completá tu ritual" siguen funcionando.
- [ ] Compra de prueba completa (checkout) antes de publicar.

Cuando esto esté OK, avisame y seguimos con la Fase 2 (split de catálogo por aroma) —
esa la dejamos afuera de este paso a propósito.
