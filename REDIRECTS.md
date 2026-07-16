# Redirects 301 — split de aromas (Giulié)

Al partir cada producto-madre "The Hood" en productos por-aroma, los handles viejos
dejan de existir (los productos-madre se **ocultan**, no se borran). Para no perder
SEO ni romper links de pauta/mails, hay que cargar estos **301** en:

**Dashboard Tiendanube → Configuración → Redirecciones (o SEO → Redirecciones 301).**

Destino recomendado = **la categoría** (seguro para SEO; evita mandar a un aroma
arbitrario). Si preferís, se puede apuntar al aroma más vendido de cada línea.

| Handle viejo (origen) | Destino 301 (categoría) |
|---|---|
| `/productos/difusor-the-hood/` | `/difusores/` |
| `/productos/home-spray-the-hood/` | `/home-spray/` |
| `/productos/vela-the-hood/` | `/velas/` |
| `/productos/vela-noir-the-hood-m69b0/` | `/velas/` |
| `/productos/refill1/` | `/refill/` |

Categorías (id → handle, verificadas): Difusores `35073734` → `/difusores/` ·
Home Spray `35073736` → `/home-spray/` · Velas `35073741` → `/velas/` ·
Refill `35254084` → `/refill/` · Accesorios `35254072` → `/accesorios/`.

**Productos que NO cambian de handle** (no requieren redirect): Varillas de Rattan
(`/varillas/`), Kit I, Kit II.

## Alternativa (destino = aroma top de la línea)
Si se prefiere mandar a producto en vez de categoría (mejor CTR, peor si ese aroma
queda sin stock), usar el más vendido por línea (datos Tiendanube):
- difusor-the-hood → `/productos/difusor-carnaby/`
- home-spray-the-hood → `/productos/home-spray-bloomsbury/`
- vela-the-hood → `/productos/vela-coconut-vanilla/`
- refill1 → `/productos/refill-carnaby/`

## Orden operativo
1. Correr `split_aromas.py` (APPLY) → crear los productos por-aroma (ocultos).
2. Revisar y publicar los nuevos en el preview de Rio.
3. **Recién ahí** ocultar los madre (`HIDE_SOURCE=1` o a mano) y cargar estos 301.
4. Verificar cada 301 en el navegador. Tiendanube regenera el sitemap solo.
