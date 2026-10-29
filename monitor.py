import os
import requests
from bs4 import BeautifulSoup
import hashlib

# Intentaremos la URL principal y alternativas automáticamente si falla
URLS_A_PROBAR = [
    "https://www.gob.mx/afac/acciones-y-programas/concesionarios-permisionarios-y-operadores-aereos-co",
    "https://www.gob.mx/afac/acciones-y-programas/concesionarios-permisionarios-y-operadores-aereos",
    "https://www.gob.mx/afac"
]

HISTORIAL_FILE = "ultimo_estado.txt"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Faltan credenciales de Telegram.")
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
        print(f"Error Telegram: {e}")

def obtener_contenido():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for url in URLS_A_PROBAR:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                print(f"Página obtenida con éxito desde: {url}")
                soup = BeautifulSoup(response.text, "html.parser")
                main_content = soup.find("main") or soup.find("div", class_="container")
                if main_content:
                    for tag in main_content(["script", "style", "footer", "nav"]):
                        tag.decompose()
                    return main_content.get_text(separator="\n", strip=True), url
        except Exception as err:
            print(f"Error al probar {url}: {err}")
            
    return "", ""

def monitorear():
    contenido_actual, url_exitosa = obtener_contenido()
    
    if not contenido_actual:
        print("No se pudo extraer contenido de ninguna URL. Finalizando sin error.")
        return

    hash_actual = hashlib.sha256(contenido_actual.encode("utf-8")).hexdigest()
    
    if not os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
            f.write(hash_actual)
        print("Primera ejecución guardada correctamente.")
        enviar_telegram("🟢 <b>Monitor AFAC activado</b>: El sistema ya está funcionando.")
        return

    with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
        hash_previo = f.read().strip()

    if hash_actual != hash_previo:
        print("¡Cambio detectado!")
        mensaje = (
            "🚨 <b>¡Actualización detectada en la AFAC!</b>\n\n"
            f"La página ha sido modificada.\n"
            f"Enlace: {url_exitosa}"
        )
        enviar_telegram(mensaje)
        
        with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
            f.write(hash_actual)
    else:
        print("Sin cambios el día de hoy.")

if __name__ == "__main__":
    monitorear()
