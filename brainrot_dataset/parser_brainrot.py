import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

# 1. Definisci qui la lista delle pagine Fandom da processare

# Carica il JSON direttamente in DataFrame
df = pd.read_json('links.json')

# Estrai la colonna 'link' come lista
URLS = df['link'].tolist()

# 2. Cartella di destinazione
OUT_DIR = "downloaded_images"
os.makedirs(OUT_DIR, exist_ok=True)

def extract_image_url(soup, page_url):
    # prova a prendere il <a href> full-res
    link = soup.find("a", href=re.compile(r"/revision/latest"))
    if link and link.get("href"):
        img_url = link["href"]
    else:
        # fallback: prendi il JSON-LD
        script = soup.find("script", type="application/ld+json")
        if not script:
            return None
        data = json.loads(script.string)
        img_url = data.get("image") or (data.get("mainEntity") or {}).get("image")
    if not img_url:
        return None
    # normalizza eventuali URL protocol-relative o site-relative
    if img_url.startswith("//"):
        img_url = "https:" + img_url
    elif img_url.startswith("/"):
        img_url = urljoin(page_url, img_url)
    return img_url

def download_image(page_url):
    try:
        resp = requests.get(page_url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"✗ Errore fetching {page_url}: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    img_url = extract_image_url(soup, page_url)
    if not img_url:
        print(f"⚠️  Immagine non trovata in {page_url}")
        return

    # estrai il percorso “pulito” dell'immagine (prima di query e /revision)
    base = img_url.split("?", 1)[0].split("/revision/", 1)[0]

    # ---- CAMBIAMENTO QUI: usa lo slug della pagina per il filename ----
    # slug della pagina (es. 'Brr_Brr_Patapim') in minuscolo
    page_slug = os.path.basename(page_url).lower()
    # estensione originale (es. '.png')
    _, ext = os.path.splitext(base)
    # nome file = slug + estensione
    filename = f"{page_slug}{ext or '.png'}"
    # ------------------------------------------------------------------

    out_path = os.path.join(OUT_DIR, filename)

    try:
        img_resp = requests.get(img_url, timeout=10)
        img_resp.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(img_resp.content)
        print(f"✓ Salvata: {out_path}")
    except Exception as e:
        print(f"✗ Errore download {img_url}: {e}")

def main():
    for page_url in URLS:
        print(f"==> Processando: {page_url}")
        download_image(page_url)

if __name__ == "__main__":
    main()
