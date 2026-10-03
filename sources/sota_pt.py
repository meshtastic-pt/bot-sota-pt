
import os
import re
import requests
from config.regions_ct import REGIOES_CT

SOTA_TOKEN_URL = "https://sso.sota.org.uk/auth/realms/SOTA/protocol/openid-connect/token"
SOTA_API_URL = "https://api-db2.sota.org.uk/api/spots"
SOTA_CLIENT_ID = "sotawatch"

def parse_ref(ref):
    r = (ref or "").strip().upper()
    if r.startswith("CT/"): r = r[3:]
    elif r.startswith("CT-"): r = r[3:]
    m = re.fullmatch(r"([A-Z]{2})-(\d{3})", r)
    return (m.group(1), m.group(2)) if m else (None, None)

def validar_ref_ct(ref):
    regiao, cume = parse_ref(ref)
    if not regiao or regiao not in REGIOES_CT:
        return False, "Referência CT inválida ou região desconhecida."
    return True, None

def obter_token():
    user, password = os.getenv("SOTA_USER"), os.getenv("SOTA_PASS")
    if not user or not password:
        return None
    r = requests.post(SOTA_TOKEN_URL, data={
        "client_id": SOTA_CLIENT_ID, "username": user, "password": password,
        "grant_type": "password"
    }, timeout=15)
    r.raise_for_status()
    return r.json().get("access_token")

def publicar_spot(activator, ref, frequencia, modo, comentario=""):
    ok, err = validar_ref_ct(ref)
    if not ok:
        return f"❌ {err}"
    regiao, cume = parse_ref(ref)
    token = obter_token()
    if not token:
        return "❌ Credenciais SOTA não configuradas."
    payload = {
        "activatorCallsign": activator, "associationCode": "CT",
        "summitCode": cume, "frequency": frequencia, "mode": modo.upper(),
        "comments": comentario or "", "posterCallsign": os.getenv("SOTA_USER", "")
    }
    r = requests.post(SOTA_API_URL, json=payload, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"
    }, timeout=15)
    if r.status_code in (200, 201):
        return f"✅ Spot SOTA publicado: {activator} CT/{regiao}-{cume} {frequencia}MHz {modo.upper()}"
    return f"❌ SOTA HTTP {r.status_code}: {r.text[:180]}"
