import os
import requests
from bs4 import BeautifulSoup
import hashlib

URL = "https://www.gob.mx/afac/acciones-y-programas/concesionarios-permisionarios-y-operadores-aereos-co"
HISTORIAL_FILE = "ultimo_estado.txt"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Faltan las credenciales de Telegram.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def obtener_contenido():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    main_content = soup.find("main") or soup.find("div", class_="container")
    
    if main_content:
        for tag in main_content(["script", "style", "footer", "nav"]):
            tag.decompose()
        return main_content.get_text(separator="\n", strip=True)
    return ""

def monitorear():
    contenido_actual = obtener_contenido()
    hash_actual = hashlib.sha256(contenido_actual.encode("utf-8")).hexdigest()
    
    if not os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
            f.write(hash_actual)
        print("Primera ejecución: Estado inicial guardado.")
        enviar_telegram("🟢 <b>Monitor AFAC activado</b>: El sistema ha comenzado a monitorear la página.")
        return

    with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
        hash_previo = f.read().strip()

    if hash_actual != hash_previo:
        print("¡Cambio detectado!")
        mensaje = (
            "🚨 <b>¡Actualización detectada en la AFAC!</b>\n\n"
            f"La página ha sufrido cambios.\n"
            f"Enlace: {URL}"
        )
        enviar_telegram(mensaje)
        
        with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
            f.write(hash_actual)
    else:
        print("Sin cambios el día de hoy.")

if __name__ == "__main__":
    monitorear()
