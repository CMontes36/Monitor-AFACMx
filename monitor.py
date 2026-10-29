import os
import requests
from bs4 import BeautifulSoup
import hashlib

# Usamos la URL base oficial sin redirección
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
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Error al enviar mensaje a Telegram: {e}")

def obtener_contenido():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    # allow_redirects=True le permite a Python seguir el enlace correcto si gob.mx lo redirige
    response = requests.get(URL, headers=headers, allow_redirects=True, timeout=20)
    
    # Si la URL redirige y da 404, probamos la URL alternativa automáticamente
    if response.status_code == 404:
        url_alt = "https://www.gob.mx/afac/acciones-y-programas/concesionarios-permisionarios-y-operadores-aereos"
        response = requests.get(url_alt, headers=headers, allow_redirects=True, timeout=20)

    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    main_content = soup.find("main") or soup.find("div", class_="container")
    
    if main_content:
        for tag in main_content(["script", "style", "footer", "nav"]):
            tag.decompose()
        return main_content.get_text(separator="\n", strip=True)
    return ""

def monitorear():
    try:
        contenido_actual = obtener_contenido()
        hash_actual = hashlib.sha256(contenido_actual.encode("utf-8")).hexdigest()
        
        if not os.path.exists(HISTORIAL_FILE):
            with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
                f.write(hash_actual)
            print("Primera ejecución completada exitosamente.")
            enviar_telegram("🟢 <b>Monitor AFAC activado</b>: El sistema ha iniciado exitosamente.")
            return

        with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
            hash_previo = f.read().strip()

        if hash_actual != hash_previo:
            print("¡Cambio detectado!")
            mensaje = (
                "🚨 <b>¡Actualización detectada en la AFAC!</b>\n\n"
                f"La página ha sido modificada.\n"
                f"Enlace: {URL}"
            )
            enviar_telegram(mensaje)
            
            with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
                f.write(hash_actual)
        else:
            print("Sin cambios el día de hoy.")
            
    except Exception as e:
        print(f"Aviso del sistema: {e}")

if __name__ == "__main__":
    monitorear()
