# -*- coding: utf-8 -*-
"""
Giulié · Split de aromas -> un PRODUCTO independiente por aroma (todas las categorías).
Reestructura para que la grilla se vea "llena" como glodcasa (theme Rio).

Hoy: 1 producto (ej. "Difusor The Hood") con un <select> de 4 aromas.
Meta: 4 productos ("Difusor Bloomsbury", "Difusor Norwood", ...), cada uno con su
      propia URL/handle, foto, precio, stock, SEO y reseñas. El eje secundario
      (Tapa y Varillas / Varillas) se CONSERVA como variante del nuevo producto.

Seguridad (patrón de cro_fixes_2026_06_18.py):
  - PREVIEW por defecto. APPLY=1 crea los productos vía POST.
  - Backup en vivo antes de tocar. Idempotente (salta handles ya existentes).
  - ONLY=<slug> corre una sola categoría piloto (ej. ONLY=vela).
  - SOURCE=backup lee del JSON de backup (dry-run offline, sin tocar la API).
  - HIDE_SOURCE=1 (solo con APPLY) despublica los productos-madre DESPUÉS de crear.
      Por defecto NO se despublica: Franco revisa los nuevos en el preview primero.
  - SPLIT_KITS=1 también parte los kits (por defecto NO: un kit es una promo).

Uso:
  python split_aromas.py                         # PREVIEW en vivo (no muta)
  SOURCE=backup python split_aromas.py           # PREVIEW offline desde backup
  ONLY=vela APPLY=1 python split_aromas.py        # crea SOLO velas (piloto)
  APPLY=1 python split_aromas.py                 # crea todo
"""
import os, re, json, io, unicodedata, urllib.request, urllib.error
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "meta-ads-manager", ".env"))
API, UA = "2025-03", "Altiva Ads (franco.luna@altivaagencia.com)"
STORE = os.getenv("TIENDANUBE_GIULIE_STORE_ID")
TOKEN = os.getenv("TIENDANUBE_GIULIE_TOKEN")
APPLY = os.getenv("APPLY") == "1"
SOURCE = os.getenv("SOURCE", "live").lower()         # live | backup
ONLY = (os.getenv("ONLY") or "").strip().lower()      # slug de categoría piloto
HIDE_SOURCE = os.getenv("HIDE_SOURCE") == "1"
SPLIT_KITS = os.getenv("SPLIT_KITS") == "1"

BASE = os.path.dirname(__file__)
BKDIR = r"C:/Users/franc/OneDrive/Documentos/FRAN ORGANIZADO/MARKETING/GENERALISTA/CLIENTES/GIULIE/tienda-api"
BACKUP = os.path.join(BKDIR, "backup_products_2026-06-12.json")
STAMP = "2026-07-07-split"

# ---- Aromas canónicos (corrige typos: Lavander->Lavender, Vainilla->Vanilla, Black pepper->Black Pepper) ----
CANON = {
    "incense & black pepper": "Incense & Black Pepper",
    "raspberry & blackberry": "Raspberry & Blackberry",
    "lavander & iris": "Lavender & Iris",
    "coconut & vainilla": "Coconut & Vanilla",
    "coconut & vanilla": "Coconut & Vanilla",
    "mango & maracuya": "Mango & Maracuyá",
    "bloomsbury": "Bloomsbury", "norwood": "Norwood",
    "carnaby": "Carnaby", "whitehall": "Whitehall",
}
# Notas olfativas por aroma (brief Giulié). El resto usa el propio nombre como nota.
NOTAS = {
    "Bloomsbury": "Vainilla & Toffee — dulce, gourmand, envolvente.",
    "Norwood": "Cardamomo, Pachulí & Haba Tonka — cálido, amaderado, de mucha presencia.",
    "Carnaby": "Frambuesa, Jazmín & Lino — chispeante y luminoso.",
    "Whitehall": "Bergamota, Orquídeas & Almizcle Blanco — fresco y sofisticado.",
}

# ---- Config por producto-madre: (label del producto nuevo, prefijo de handle, splitear?) ----
# El eje "Aromas" se detecta solo; el resto de ejes se conservan como variante.
SOURCES = {
    306651767: dict(label="Difusor",   prefix="difusor",    split=True),
    306651944: dict(label="Home Spray", prefix="home-spray", split=True),
    306652171: dict(label="Vela",      prefix="vela",       split=True),
    308540371: dict(label="Refill",    prefix="refill",     split=True),
    341559578: dict(label="Vela Noir", prefix="vela-noir",  split=True),
    309366644: dict(label="Varillas",  prefix="varillas",   split=False),  # sin aroma
    325483017: dict(label="Kit I",     prefix="kit-i",      split=SPLIT_KITS),
    341151825: dict(label="Kit II",    prefix="kit-ii",     split=SPLIT_KITS),
}


def req(path, method="GET", body=None):
    url = f"https://api.tiendanube.com/{API}/{STORE}/{path}"
    data = json.dumps(body).encode() if body is not None else None
    h = {"Authentication": "bearer " + (TOKEN or ""), "User-Agent": UA}
    if data is not None:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else None
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:400]}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower().replace("&", " ").replace("/", " ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


def canon(aroma):
    return CANON.get(aroma.strip().lower(), aroma.strip())


def es(v):
    return (v or {}).get("es", "") if isinstance(v, dict) else (v or "")


def load_products():
    if SOURCE == "backup":
        return json.load(io.open(BACKUP, encoding="utf-8"))
    out, page = [], 1
    while True:
        chunk = req(f"products?per_page=200&page={page}")
        if not isinstance(chunk, list) or not chunk:
            break
        out += chunk
        if len(chunk) < 200:
            break
        page += 1
    return out


def aroma_axis_index(prod):
    """Índice del eje de atributo cuyo nombre contiene 'aroma'."""
    for i, a in enumerate(prod.get("attributes") or []):
        if "aroma" in es(a).strip().lower():
            return i
    return None


def build_plan(prod, cfg):
    """Devuelve lista de payloads de producto-nuevo por aroma."""
    ai = aroma_axis_index(prod)
    if ai is None:
        return []
    attrs = prod.get("attributes") or []
    other_idx = [i for i in range(len(attrs)) if i != ai]
    cat_ids = [c["id"] for c in (prod.get("categories") or []) if c.get("id")]
    imgs = {im["id"]: im.get("src") for im in (prod.get("images") or [])}

    # agrupar variantes por aroma canónico
    by_aroma = {}
    for v in prod.get("variants") or []:
        vals = v.get("values") or []
        if ai >= len(vals):
            continue
        aroma = canon(es(vals[ai]))
        by_aroma.setdefault(aroma, []).append(v)

    plans = []
    for aroma, vlist in by_aroma.items():
        name = f"{cfg['label']} {aroma}"
        handle = f"{cfg['prefix']}-{slug(aroma)}"
        # variantes del nuevo producto: conservar ejes secundarios
        new_variants = []
        img_src = None
        for v in vlist:
            vals = v.get("values") or []
            sec = [{"es": es(vals[i])} for i in other_idx if i < len(vals)]
            nv = {"price": v.get("price"), "stock": v.get("stock")}
            if v.get("weight"): nv["weight"] = v.get("weight")
            if sec: nv["values"] = sec
            new_variants.append(nv)
            if img_src is None:
                img_src = imgs.get(v.get("image_id"))
        nota = NOTAS.get(aroma, f"{aroma}.")
        desc = (f"<p><strong>{cfg['label']} '{aroma}'</strong> de la colección The Hood. "
                f"Aroma de autor para transformar tu ambiente.</p>"
                f"<p><strong>Notas:</strong> {nota}</p>")
        payload = {
            "name": {"es": name},
            "handle": {"es": handle},
            "description": {"es": desc},
            "categories": cat_ids,
            "attributes": [attrs[i] for i in other_idx],   # sin "Aromas"
            "variants": new_variants,
            "seo_title": {"es": f"{name} | Giulié"},
            "seo_description": {"es": f"{cfg['label']} aroma {aroma}. {nota}"},
            "published": False,   # se crean OCULTOS; Franco los revisa y publica
        }
        if img_src:
            payload["images"] = [{"src": img_src}]
        plans.append((handle, name, len(new_variants), img_src is not None, payload))
    return plans


def main():
    if not STORE or not TOKEN:
        print("!! Falta TIENDANUBE_GIULIE_STORE_ID/_TOKEN en meta-ads-manager/.env")
        if SOURCE != "backup":
            return
    print(f"MODO: {'APPLY (crea productos)' if APPLY else 'PREVIEW (no muta)'} | SOURCE={SOURCE}"
          f"{' | ONLY='+ONLY if ONLY else ''} | SPLIT_KITS={SPLIT_KITS}\n")

    prods = load_products()
    byid = {p["id"]: p for p in prods}
    existing_handles = {es(p.get("handle")) for p in prods}

    all_plans, redirects = [], []
    total_new = 0
    for pid, cfg in SOURCES.items():
        prod = byid.get(pid)
        if not prod:
            print(f"[{pid}] {cfg['label']}: NO está en el catálogo cargado — skip")
            continue
        if not cfg["split"]:
            print(f"[{pid}] {cfg['label']}: NO se splitea (sin aroma o kit) — se deja igual\n")
            continue
        if ONLY and cfg["prefix"] != ONLY and slug(cfg["label"]) != ONLY:
            continue
        plans = build_plan(prod, cfg)
        if not plans:
            print(f"[{pid}] {cfg['label']}: sin eje 'Aromas' detectable — skip\n")
            continue
        old_handle = es(prod.get("handle"))
        cat_ids = [c["id"] for c in (prod.get("categories") or []) if c.get("id")]
        print(f"[{pid}] {cfg['label']}  (madre handle={old_handle})  -> {len(plans)} productos nuevos:")
        for handle, name, nvar, hasimg, _ in plans:
            dup = "  [YA EXISTE -> skip]" if handle in existing_handles else ""
            print(f"    · {name:32s} /{handle:28s} variantes={nvar} img={'sí' if hasimg else 'NO'}{dup}")
        # redirect madre -> primera categoría (o /productos/ si no hay)
        dest = f"/categoria/{cat_ids[0]}" if cat_ids else "/productos/"
        redirects.append({"from": f"/productos/{old_handle}/", "to_category_id": cat_ids[0] if cat_ids else None})
        all_plans += [(pid, p) for p in plans]
        total_new += len(plans)
        print()

    print(f"RESUMEN: {total_new} productos nuevos a crear "
          f"(de {sum(1 for _,c in SOURCES.items() if c['split'])} madres splitteables).\n")

    if not APPLY:
        print("(PREVIEW) Nada creado. Revisá el plan y corré con APPLY=1 (idealmente ONLY=<cat> primero).")
        # dejar el plan de redirects a mano para cargarlos en Dashboard -> Redirecciones
        io.open(os.path.join(BASE, "redirects_split.json"), "w", encoding="utf-8").write(
            json.dumps(redirects, ensure_ascii=False, indent=2))
        print(f"redirects (borrador) -> {os.path.join(BASE, 'redirects_split.json')}")
        return

    # ---- APPLY ----
    if SOURCE == "backup":
        print("!! APPLY requiere SOURCE=live (no crear desde un backup viejo). Abort."); return
    json.dump(prods, io.open(f"{BKDIR}/backup_products_{STAMP}.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"backup en vivo -> {BKDIR}/backup_products_{STAMP}.json\n--- CREANDO ---")
    created = []
    for pid, (handle, name, nvar, hasimg, payload) in all_plans:
        if handle in existing_handles:
            print(f"skip (existe): {handle}"); continue
        r = req("products", "POST", payload)
        ok = isinstance(r, dict) and r.get("id") and not r.get("_error")
        print(f"{'OK ' if ok else 'ERR'} {name} /{handle}: {r.get('id') if ok else r}")
        if ok:
            created.append({"source": pid, "id": r["id"], "handle": handle, "name": name})
    json.dump(created, io.open(os.path.join(BASE, f"created_{STAMP}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\ncreados: {len(created)} -> {os.path.join(BASE, f'created_{STAMP}.json')}")

    if HIDE_SOURCE and created:
        print("\n--- DESPUBLICANDO madres (HIDE_SOURCE=1) ---")
        for pid in {c['source'] for c in created}:
            r = req(f"products/{pid}", "PUT", {"published": False})
            print(f"madre {pid}: {'oculto' if not r.get('_error') else r}")


if __name__ == "__main__":
    main()
