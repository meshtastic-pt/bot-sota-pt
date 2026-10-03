
import requests
from bs4 import BeautifulSoup

SGIFR_URL = "https://www.sgifr.gov.pt/"
ANEPC_URL = "https://prociv.gov.pt/pt/avisos-a-populacao/"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Meshtastic-PT-Bot/1.0"})

def ocorrencias_ativas():
    try:
        r = SESSION.get(SGIFR_URL, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        if "Ocorrências Ativas" not in text:
            return []
        return [{"raw": text.split("Ocorrências Ativas", 1)[1][:12000],
                 "source": "SGIFR"}]
    except Exception:
        return []

def avisos_anepc():
    try:
        r = SESSION.get(ANEPC_URL, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        return [x.get_text(" ", strip=True)
                for x in soup.select("article, .card, li")
                if x.get_text(strip=True)]
    except Exception:
        return []
