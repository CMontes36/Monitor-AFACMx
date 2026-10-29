import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.gob.mx/afac/acciones-y-programas/concesionarios-permisionarios-y-operadores-aereos-co"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"})

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
req = requests.get(URL, headers=headers)

if req.status_code == 200:
    print("¡Conexión exitosa a la AFAC!")
    enviar_telegram("🟢 <b>Prueba AFAC</b>: Conexión realizada con éxito.")
else:
    print(f"Respuesta del servidor: {req.status_code}")
