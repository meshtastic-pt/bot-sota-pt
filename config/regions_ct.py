
# Regiões SOTA de Portugal continental (CT)
REGIOES_CT = {
    "AA": "Alto Alentejo",
    "AL": "Algarve",
    "BA": "Beira Alta",
    "BB": "Beira Baixa",
    "BL": "Beira Litoral",
    "BT": "Baixo Alentejo",
    "DL": "Douro Litoral",
    "ES": "Estremadura",
    "MN": "Minho",
    "RB": "Ribatejo",
    "TM": "Trás-os-Montes e Alto Douro",
}
SOTA_ASSOCIATION = "CT"

def normalizar_regiao(valor):
    if not valor:
        return None
    v = valor.strip().upper().replace("CT/", "").replace("CT-", "")
    return v if v in REGIOES_CT else None

def nome_regiao(valor):
    codigo = normalizar_regiao(valor)
    return REGIOES_CT.get(codigo, codigo)

def parse_sota_ref(ref):
    """CT/AL-001, CT-AL-001 ou AL-001 -> ('CT','AL','001')."""
    import re
    if not ref:
        return None, None, None
    r = ref.strip().upper()
    if r.startswith("CT/"):
        r = r[3:]
    elif r.startswith("CT-"):
        r = r[3:]
    m = re.fullmatch(r"([A-Z]{2})-(\d{3})", r)
    if not m:
        return None, None, None
    regiao, cume = m.groups()
    return "CT", regiao, cume

def canal_regiao(codigo):
    codigo = normalizar_regiao(codigo)
    return f"CT-{codigo}" if codigo else None
