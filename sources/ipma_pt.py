
import requests
from datetime import datetime

BASE = "https://api.ipma.pt/open-data"
WARNINGS_URL = f"{BASE}/forecast/warnings/warnings_www.json"
SEISMIC_URL = f"{BASE}/observation/seismic/7.json"
LOCATIONS_URL = f"{BASE}/distrits-islands.json"
STATIONS_URL = f"{BASE}/observation/meteorology/stations/stations.json"
OBSERVATIONS_URL = f"{BASE}/observation/meteorology/stations/observations.json"
DAILY_URL = f"{BASE}/forecast/meteorology/cities/daily/{{}}.json"
RCM_URL = f"{BASE}/forecast/meteorology/rcm/rcm-d{{}}.json"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Meshtastic-PT-Bot/1.0"})
LOCATIONS = None
STATIONS = None

def _get(url, timeout=20):
    r = SESSION.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()

def carregar_locais():
    global LOCATIONS
    if LOCATIONS is None:
        LOCATIONS = _get(LOCATIONS_URL).get("data", [])
    return LOCATIONS

def local_mais_proximo(lat, lon):
    best, best_d = None, float("inf")
    for x in carregar_locais():
        try:
            d = (float(x["latitude"])-lat)**2 + (float(x["longitude"])-lon)**2
            if d < best_d:
                best, best_d = x, d
        except (KeyError, TypeError, ValueError):
            pass
    return best

def carregar_estacoes():
    global STATIONS
    if STATIONS is None:
        data = _get(STATIONS_URL)
        STATIONS = []
        for f in data:
            p = f.get("properties", {})
            c = (f.get("geometry") or {}).get("coordinates") or []
            if len(c) >= 2:
                STATIONS.append({
                    "id": p.get("idEstacao"),
                    "name": p.get("localEstacao"),
                    "lon": float(c[0]),
                    "lat": float(c[1]),
                })
    return STATIONS

def estacao_mais_proxima(lat, lon):
    best, best_d = None, float("inf")
    for s in carregar_estacoes():
        d = (s["lat"]-lat)**2 + (s["lon"]-lon)**2
        if d < best_d:
            best, best_d = s, d
    return best

def observacao_atual(lat, lon):
    station = estacao_mais_proxima(lat, lon)
    if not station:
        return None
    data = _get(OBSERVATIONS_URL)
    # observations.json usa timestamps como chaves e idEstacao como subchave.
    for timestamp in sorted(data.keys(), reverse=True):
        obs = data.get(timestamp, {}).get(str(station["id"]))
        if obs:
            return {
                "timestamp": timestamp,
                "station": station,
                "data": obs,
            }
    return None

def previsao_local(lat, lon):
    local = local_mais_proximo(lat, lon)
    if not local:
        return None
    data = _get(DAILY_URL.format(local["globalIdLocal"]))
    return {"local": local, "data": data.get("data", [])}

def dados_clima_compat(lat, lon):
    """Devolve uma estrutura semelhante à usada pelo bot original."""
    obs = observacao_atual(lat, lon)
    prev = previsao_local(lat, lon)
    if not obs and not prev:
        return None

    o = obs["data"] if obs else {}
    forecast = (prev or {}).get("data", [])

    def num(v):
        try: return float(v)
        except (TypeError, ValueError): return None

    wind_kmh = num(o.get("intensidadeVentoKM"))
    temp = num(o.get("temperatura"))
    humidity = num(o.get("humidade"))
    pressure = num(o.get("pressao"))
    wind_dir_class = o.get("idDireccVento")

    direction_map = {
        0: 0, 1: 0, 2: 45, 3: 90, 4: 135,
        5: 180, 6: 225, 7: 270, 8: 315, 9: 0
    }
    wind_dir = direction_map.get(int(wind_dir_class), 0) if wind_dir_class not in (None, "-99.0") else 0

    daily = {
        "time": [x.get("forecastDate") for x in forecast],
        "weather_code": [x.get("idWeatherType") for x in forecast],
        "temperature_2m_max": [num(x.get("tMax")) for x in forecast],
        "temperature_2m_min": [num(x.get("tMin")) for x in forecast],
        "wind_direction_10m_dominant": [0 for _ in forecast],
        "wind_gusts_10m_max": [None for _ in forecast],
    }

    return {
        "current": {
            "temperature_2m": temp,
            "relative_humidity_2m": humidity,
            "weather_code": 0,
            "wind_speed_10m": wind_kmh,
            "wind_direction_10m": wind_dir,
            "surface_pressure": pressure,
        },
        "daily": daily,
        "ipma_station": (obs or {}).get("station", {}),
        "ipma_forecast": prev or {},
    }

def avisos():
    return _get(WARNINGS_URL)

def sismos():
    return _get(SEISMIC_URL).get("data", [])

def risco_incendio(dia=0):
    return _get(RCM_URL.format(dia))

def descricao_risco(rcm):
    return {
        1: "Reduzido", 2: "Moderado", 3: "Elevado",
        4: "Muito elevado", 5: "Máximo"
    }.get(int(rcm), "Desconhecido")
