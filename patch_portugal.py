
#!/usr/bin/env python3
from pathlib import Path
import re, shutil

SRC = Path("bot_meshtastic.py")
if not SRC.exists():
    raise SystemExit("Execute na raiz do clone bot-ea7.")
text = SRC.read_text(encoding="utf-8")
backup = SRC.with_name("bot_meshtastic.py.pre-portugal")
if not backup.exists():
    shutil.copy2(SRC, backup)

def between(s, start, end, label):
    a = s.find(start)
    b = s.find(end, a)
    if a < 0 or b < 0:
        raise RuntimeError(f"Bloco não encontrado: {label}")
    return s[:a] + s[b:]

# Gasolina
text = between(text, "def obtener_precios_gasolina(", "def _qrz_ns(", "gasolina")

# Routers/nodes fixos
text = re.sub(r'ROUTERS_VIGILADOS\s*=\s*\{.*?\n\}\n',
              'ROUTERS_VIGILADOS = {}\n', text, flags=re.S)
text = re.sub(r'NODOS_INFO2\s*=\s*\{.*?\}\n',
              'NODOS_INFO2 = {}\n', text, count=1, flags=re.S)

# Regiões SOTA CT; remove municípios espanhóis.
a = text.find("# --- CONFIGURACIÓN MULTIPROVINCIA ---")
b = text.find("# --- MUNICIPIOS (con provincia) ---", a)
if a < 0 or b < 0:
    raise RuntimeError("Configuração de províncias não encontrada.")
cfg = '''# --- CONFIGURAÇÃO REGIONAL PORTUGAL / SOTA CT ---
from config.regions_ct import REGIOES_CT, parse_sota_ref
PROVINCIAS = {k: {"channel_name": f"CT-{k}", "nome": v}
              for k, v in REGIOES_CT.items()}
CANALES = {k: v["channel_name"] for k, v in PROVINCIAS.items()}
CHANNEL_TO_PROV = {}
CHANNEL_NAMES = {}
TOWNS = []
'''
text = text[:a] + cfg + text[b:]

# IPMA sismos no lugar do EMSC.
a = text.find("# --- TRABAJADOR TERREMOTOS (EMSC) ---")
b = text.find("# --- TRABAJADOR INCENDIOS FORESTALES (FIRMS/NASA) ---", a)
if a < 0 or b < 0:
    raise RuntimeError("Worker EMSC não encontrado.")
worker = '''# --- TRABALHADOR SISMOS IPMA ---
from sources import ipma_pt
def terremotos_worker(iface):
    while True:
        try:
            for ev in ipma_pt.sismos():
                ev_id = f"IPMA-{ev.get('time')}-{ev.get('lat')}-{ev.get('lon')}"
                mag = ev.get("magnitud", "N/A")
                try: magnitude = float(mag)
                except (TypeError, ValueError): magnitude = 0.0
                conn = sqlite3.connect(DB_PATH, timeout=10)
                c = conn.cursor()
                c.execute("SELECT 1 FROM terremotos WHERE id = ?", (ev_id,))
                if c.fetchone():
                    conn.close()
                    continue
                c.execute("INSERT INTO terremotos (id,magnitud,ubicacion,fecha) VALUES (?,?,?,?)",
                          (ev_id, mag, ev.get("obsRegion") or ev.get("local") or "Portugal", ev.get("time","")))
                conn.commit(); conn.close()
                if magnitude < MIN_MAGNITUD_TERREMOTO:
                    continue
                msg = f"🏔️ SISMO M{magnitude:.1f}\\n📍 {ev.get('obsRegion') or ev.get('local') or 'Portugal'}\\n🕐 {ev.get('time','')}"
                iface.sendText(msg, destinationId=meshtastic.BROADCAST_ADDR,
                               channelIndex=0, wantAck=False)
                enviar_telegram(f"📢 *SISMO IPMA M{magnitude:.1f}*\\n`{msg}`", MI_CHAT_ID)
        except Exception as e:
            logging.error(f"IPMA sismos: {e}")
        time.sleep(300)

'''
text = text[:a] + worker + text[b:]

# Remove both old fire workers; replace with SGIFR.
a = text.find("# --- TRABAJADOR INCENDIOS FORESTALES (FIRMS/NASA) ---")
b = text.find("# --- TRABAJADOR CALIMA (OPEN-METEO AIR QUALITY, ALERTA PROACTIVA) ---", a)
if a < 0 or b < 0:
    raise RuntimeError("Workers de incêndio não encontrados.")
fire = '''# --- TRABALHADOR INCÊNDIOS PORTUGAL / SGIFR ---
from sources import sgifr_pt
def incendios_worker(iface):
    while True:
        try:
            ocorrencias = sgifr_pt.ocorrencias_ativas()
            if ocorrencias:
                raw = ocorrencias[0].get("raw","")
                fire_id = f"SGIFR-{hash(raw[:700])}"
                conn = sqlite3.connect(DB_PATH, timeout=10)
                c = conn.cursor()
                c.execute("SELECT 1 FROM incendios_alertas WHERE fire_id=? AND date(fecha)=date('now')",
                          (fire_id,))
                seen = c.fetchone()
                if not seen:
                    c.execute("INSERT OR REPLACE INTO incendios_alertas(fire_id,fecha) VALUES (?,datetime('now'))",
                              (fire_id,))
                    conn.commit()
                conn.close()
                if not seen and time.time()-BOT_START_TIME >= 1800:
                    enviar_con_limite(iface,
                        "🔥 SGIFR — existem ocorrências de incêndio ativas.",
                        0, f"🔥 *SGIFR*\\n{raw[:900]}", MI_CHAT_ID)
        except Exception as e:
            logging.warning(f"SGIFR: {e}")
        time.sleep(1800)

'''
text = text[:a] + fire + text[b:]

# SOTA parser PT
old = '''def parsear_ref_sota(ref):
    if "/" in ref:
        partes = ref.split("/")
        if len(partes) == 2:
            return partes[0], partes[1]
    elif ref.count("-") >= 1:
        idx = ref.index("-")
        return ref[:idx], ref[idx+1:]
    return None, None
'''
new = '''def parsear_ref_sota(ref):
    assoc, regiao, summit = parse_sota_ref(ref)
    if assoc != "CT" or regiao not in REGIOES_CT:
        return None, None
    return "CT", f"{regiao}-{summit}"
'''
text = text.replace(old, new)

# Comando gasolina
text = text.replace(", /gasolina", "").replace("/gasolina, ", "")
text = re.sub(r'\n\s*elif msg_cmd == "/gasolina":.*?(?=\n\s*elif |\n\s*except |\n\s*return )',
              '', text, flags=re.S)
text = re.sub(r'\n\s*elif cmd == "/gasolina":.*?(?=\n\s*elif |\n\s*except |\n\s*return )',
              '', text, flags=re.S)

# Workers removidos
text = text.replace('threading.Thread(target=aemet_worker, args=(iface,), daemon=True).start()\n','')
text = text.replace('threading.Thread(target=infoca_worker, args=(iface,), daemon=True).start()\n','')

# Remove códigos/provincias espanholas usados exclusivamente pela gasolina
# e coordenadas espanholas usadas pelos comandos de clima.
text = re.sub(r'CODIGOS_PROVINCIAS\s*=\s*\{.*?\n\}\n', '', text, count=1, flags=re.S)
text = re.sub(r'COORDENADAS_PROVINCIAS\s*=\s*\{.*?\n\}\n', '''COORDENADAS_PROVINCIAS = {
    "aa": (39.30, -7.43), "al": (37.14, -8.54), "ba": (40.64, -7.91),
    "bb": (39.82, -7.50), "bl": (40.21, -8.43), "bt": (38.15, -7.58),
    "dl": (41.15, -8.61), "es": (38.72, -9.14), "mn": (41.69, -8.83),
    "rb": (39.46, -8.54), "tm": (41.55, -7.43),
} 
''', text, count=1, flags=re.S)

# Clima: manter as funções e formato do bot, mas obter os dados no IPMA.
a = text.find("def obtener_datos_clima(")
b = text.find("def obtener_clima_espacial(", a)
if a >= 0 and b >= 0:
    text = text[:a] + '''def obtener_datos_clima(lat=37.1363, lon=-8.5375):
    try:
        from sources.ipma_pt import dados_clima_compat
        return dados_clima_compat(lat, lon)
    except Exception as e:
        logging.warning(f"IPMA clima: {e}")
        return None
''' + text[b:]

# Espanha -> Portugal
text = text.replace('ZoneInfo("Europe/Madrid")', 'ZoneInfo("Europe/Lisbon")')
text = text.replace('(36.83, -2.45)', '(37.1363, -8.5375)')
text = text.replace('"Almeria"', '"AL"').replace('"almeria"', '"al"')

# Evita contagem de routers fixos no status.
text = re.sub(r'rt_on\s*=\s*sum\(1 for rid in ROUTERS_VIGILADOS.*?\)\n', '', text, flags=re.S)
text = text.replace('f"📍 Routers: {rt_on}/{len(ROUTERS_VIGILADOS)} 🟢\\n"',
                    'f"📡 Rede: {nodos_tot} nós conhecidos\\n"')
text = text.replace('f"📍 *Routers:* `{rt_on}/{len(ROUTERS_VIGILADOS)}` 🟢\\n"',
                    'f"📡 *Rede:* `{nodos_tot}` nós conhecidos\\n"')

SRC.write_text(text, encoding="utf-8")
print("OK — backup:", backup)
print("Reveja: git diff -- bot_meshtastic.py")
