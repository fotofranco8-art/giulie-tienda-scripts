#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy script CRO a Tiendanube vía Portal de Partners.

Uso:
  python deploy_script.py                 # PREVIEW (muestra qué va a cambiar)
  APPLY=1 python deploy_script.py         # APPLY (pushea a Producción)
"""
import os, json, urllib.request, urllib.error
from dotenv import load_dotenv

# Cargar .env desde la carpeta meta-ads-manager (parent)
env_path = os.path.join(os.path.dirname(__file__), "..", "meta-ads-manager", ".env")
load_dotenv(env_path)

SCRIPT_ID = "7481"
SCRIPT_FILE = "giulie-cro.js"
API_ENDPOINT = "https://api.tiendanube.com/v1/apps/scripts/{id}/versions"

APP_ID = os.getenv("TIENDANUBE_CLIENT_ID")
APP_SECRET = os.getenv("TIENDANUBE_CLIENT_SECRET")
APPLY = os.getenv("APPLY") == "1"

def read_script():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def deploy_version(script_content):
    """Crea nueva versión en Tiendanube."""
    url = API_ENDPOINT.format(id=SCRIPT_ID)
    payload = {
        "src_content": script_content,
        "description": "Fase 2: descripciones colapsadas + acordeón Elegí tu estilo (2026-07-16)"
    }

    # Usar Client ID:Secret para autenticación básica
    import base64
    auth_str = base64.b64encode(f"{APP_ID}:{APP_SECRET}".encode()).decode()
    h = {
        "Authorization": f"Basic {auth_str}",
        "Content-Type": "application/json"
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=h, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            return result
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:400]}

def main():
    if not APP_ID or not APP_SECRET:
        print("❌ Falta TIENDANUBE_CLIENT_ID o TIENDANUBE_CLIENT_SECRET en .env")
        return

    script_content = read_script()
    print(f"Leyendo script: {SCRIPT_FILE} ({len(script_content)} bytes)\n")

    if APPLY:
        print("🚀 DEPLOYANDO a Producción...\n")
        result = deploy_version(script_content)
        if result.get("id"):
            print(f"✅ ÉXITO — Nueva versión: {result['version']}")
            print(f"   URL: {result.get('src', 'N/A')}")
        else:
            print(f"❌ ERROR — {result}")
    else:
        print("📋 PREVIEW — Script listo para deploy.")
        print(f"   Ejecutar con: APPLY=1 python deploy_script.py")

if __name__ == "__main__":
    main()
