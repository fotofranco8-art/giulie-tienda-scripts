# -*- coding: utf-8 -*-
"""
Giulié · Actualiza descripciones de productos post-split con copy personalizado.
Usa el template PDP de copy-tienda-giulie.md + notas olfativas por aroma.

Modo PREVIEW: descarga los productos nuevos y muestra qué va a cambiar.
Modo APPLY=1: actualiza vía API (PATCH /products/{id}).

Uso:
  python update_descriptions.py                 # PREVIEW
  APPLY=1 python update_descriptions.py         # aplica cambios
  ONLY=difusor-bloomsbury APPLY=1 python update_descriptions.py  # solo un producto
"""
import os, re, json, io, urllib.request, urllib.error
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "meta-ads-manager", ".env"))
API, UA = "2025-03", "Altiva Ads (franco.luna@altivaagencia.com)"
STORE = os.getenv("TIENDANUBE_GIULIE_STORE_ID")
TOKEN = os.getenv("TIENDANUBE_GIULIE_TOKEN")
APPLY = os.getenv("APPLY") == "1"
ONLY = (os.getenv("ONLY") or "").strip().lower()

# Descripciones personalizadas por tipo de producto + aroma
TEMPLATES = {
    "difusor": {
        "intro": "Tu ambiente, con una firma propia.",
        "beneficio": "El Difusor The Hood perfuma tu casa de forma constante y elegante, sin humo ni fuego. Lo prendés una vez y te acompaña todo el día.",
        "specs": "200 ml · varillas de rattan incluidas · dura aprox. 30 a 45 días.",
    },
    "home-spray": {
        "intro": "Un gesto, tu ambiente renovado.",
        "beneficio": "Un gesto y listo: tu ambiente renovado en segundos. El mismo aroma del difusor, en un formato rápido.",
        "specs": "Spray de 250 ml · efectivo al instante.",
    },
    "vela": {
        "intro": "Luz cálida y aroma envolvente.",
        "beneficio": "Luz cálida y aroma envolvente para tus momentos lentos. Prende y disfruta del ritual.",
        "specs": "Vela de ~50 hs de encendido en promedio.",
    },
    "refill": {
        "intro": "Tu aroma favorito, recargado.",
        "beneficio": "Tu difusor favorito, recargado. Mismo ritual, sin que el aroma se termine. Rinde hasta 2 recargas.",
        "specs": "Refill de 200 ml · sale ~$16.250 por carga vs $27.000 un difusor nuevo.",
    },
    "vela-noir": {
        "intro": "Negra, elegante, presente.",
        "beneficio": "La vela noir The Hood: negra, elegante, con presencia. Luz y aroma sofisticado para espacios que piden más.",
        "specs": "Vela negra de ~50 hs de encendido en promedio.",
    },
}

# Notas olfativas por aroma (mismo que en split_aromas.py)
NOTAS = {
    "Bloomsbury": "Vainilla & Toffee — dulce, gourmand, envolvente.",
    "Norwood": "Cardamomo, Pachulí & Haba Tonka — cálido, amaderado, de mucha presencia.",
    "Carnaby": "Frambuesa, Jazmín & Lino — chispeante y luminoso.",
    "Whitehall": "Bergamota, Orquídeas & Almizcle Blanco — fresco y sofisticado.",
}

# Descripciones por aroma (brevemente)
AROMA_INTROS = {
    "Bloomsbury": "Dulce y envolvente, como un abrazo tibio. El gourmand de la casa, para sobremesas largas y momentos lentos.",
    "Norwood": "Cálido y amaderado, con una especia que reconforta. El aroma sereno que se queda.",
    "Carnaby": "Fresco y vibrante, con un costado frutal y floral. La energía de la calle más viva de Londres.",
    "Whitehall": "Elegante y luminoso, con presencia. El que se nota sin gritar.",
    "Incense & Black Pepper": "Especiado y misterioso, con profundidad.",
    "Raspberry & Blackberry": "Frutal y jugoso, fresco y vibrante.",
    "Lavender & Iris": "Floral y relajante, minimalista y elegante.",
    "Coconut & Vanilla": "Tropical y reconfortante, dulce y cálido.",
    "Mango & Maracuyá": "Frutal y tropical, energizante y luminoso.",
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

def es(v):
    return (v or {}).get("es", "") if isinstance(v, dict) else (v or "")

def load_products():
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

def extract_type_and_aroma(handle):
    """Extrae tipo (difusor, home-spray, etc.) y aroma del handle."""
    # Patrones posibles:
    # - difusor-bloomsbury
    # - difusor-the-hood-bloomsbury (post-split con "the-hood" en medio)
    aroma_map = {
        "bloomsbury": "Bloomsbury",
        "norwood": "Norwood",
        "carnaby": "Carnaby",
        "whitehall": "Whitehall",
        "incense-black-pepper": "Incense & Black Pepper",
        "raspberry-blackberry": "Raspberry & Blackberry",
        "lavender-iris": "Lavender & Iris",
        "coconut-vanilla": "Coconut & Vanilla",
        "mango-maracuya": "Mango & Maracuyá",
    }

    for tipo in ["difusor", "home-spray", "vela-noir", "vela", "refill"]:
        # Busca: tipo-[the-hood-]aroma-slug
        import re
        m = re.match(rf"{tipo}(?:-the-hood)?-(.+)$", handle)
        if m:
            aroma_slug = m.group(1)
            aroma = aroma_map.get(aroma_slug, aroma_slug.replace("-", " ").title())
            return (tipo, aroma)
    return (None, None)

def build_description(tipo, aroma):
    """Construye HTML de descripción personalizada."""
    tmpl = TEMPLATES.get(tipo)
    if not tmpl:
        return None

    nota = NOTAS.get(aroma, "")
    aroma_intro = AROMA_INTROS.get(aroma, f"{aroma}.")

    desc = (
        f"<p><strong>{aroma_intro}</strong></p>"
        f"<p>{tmpl['beneficio']}</p>"
        f"<p><strong>Notas:</strong> {nota}</p>"
        f"<p>{tmpl['specs']}</p>"
        f"<p><small>Envío a todo el país · cambios sin costo.</small></p>"
    )
    return desc

def main():
    if not STORE or not TOKEN:
        print("!! Falta TIENDANUBE_GIULIE_STORE_ID/_TOKEN en meta-ads-manager/.env")
        return

    print(f"MODO: {'APPLY (actualiza vía API)' if APPLY else 'PREVIEW (no muta)'}")
    if ONLY:
        print(f"ONLY={ONLY}\n")
    else:
        print()

    prods = load_products()

    # Filtra productos nuevos (post-split): tienen handle con patrón "tipo-aroma"
    new_products = []
    for p in prods:
        handle = es(p.get("handle")).lower()
        tipo, aroma = extract_type_and_aroma(handle)
        if tipo and aroma:
            new_products.append((p, tipo, aroma, handle))

    print(f"Encontrados {len(new_products)} productos nuevos (post-split).\n")

    to_update = []
    for prod, tipo, aroma, handle in new_products:
        if ONLY and handle != ONLY:
            continue

        desc = build_description(tipo, aroma)
        if not desc:
            print(f"[SKIP] {handle}: template no encontrado")
            continue

        to_update.append({
            "id": prod["id"],
            "handle": handle,
            "name": es(prod.get("name")),
            "desc": desc,
        })

    if not to_update:
        print("(PREVIEW) Nada que actualizar.")
        return

    print(f"A ACTUALIZAR: {len(to_update)} productos\n")
    for upd in to_update:
        print(f"  · {upd['handle']:30s} (ID {upd['id']})")

    if not APPLY:
        print("\n(PREVIEW) Nada actualizado. Revisá el plan y corré con APPLY=1.")
        return

    # ---- APPLY ----
    print("\n--- ACTUALIZANDO DESCRIPCIONES ---\n")
    updated = []
    for upd in to_update:
        payload = {"description": {"es": upd["desc"]}}
        r = req(f"products/{upd['id']}", "PUT", payload)
        ok = isinstance(r, dict) and r.get("id") and not r.get("_error")
        status = "OK " if ok else "ERR"
        print(f"{status} {upd['handle']}: {r.get('id') if ok else r}")
        if ok:
            updated.append(upd["handle"])

    print(f"\nACTUALIZADOS: {len(updated)}/{len(to_update)}")

if __name__ == "__main__":
    main()
