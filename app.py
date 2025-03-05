import os
import sqlite3
import shutil
import time
import pyfiglet
from datetime import datetime, timedelta

# Pobierz nazwę użytkownika i określ ścieżkę do folderu Chrome
try:
    username = os.getlogin()
    chrome_dir = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\"
    history_db = os.path.join(chrome_dir, 'History')
except Exception as e:
    print(f"Błąd przy pobieraniu nazwy użytkownika lub ścieżki: {e}")
    exit(1)

# Sprawdź, czy plik bazy danych istnieje
if not os.path.exists(history_db):
    print(f"Plik bazy danych Chrome ({history_db}) nie istnieje. Upewnij się, że Chrome jest zainstalowany.")
    exit(1)

# Utwórz tymczasową kopię bazy danych
temp_history_db = os.path.join(chrome_dir, 'History_temp')
try:
    shutil.copy2(history_db, temp_history_db)  # Kopiuj plik History
except Exception as e:
    print(f"Błąd przy kopiowaniu pliku bazy danych: {e}")
    exit(1)

# Połącz się z kopią bazy danych
try:
    c = sqlite3.connect(temp_history_db)
    cursor = c.cursor()
except sqlite3.OperationalError as e:
    print(f"Błąd połączenia z bazą danych: {e}")
    os.remove(temp_history_db)  # Usuń kopię w przypadku błędu
    exit(1)

# Wykonaj zapytanie SQL
select_statement = "SELECT id, url, title, visit_count, last_visit_time FROM urls"
try:
    cursor.execute(select_statement)
    results = cursor.fetchall()
except sqlite3.Error as e:
    print(f"Błąd przy wykonywaniu zapytania SQL: {e}")
    c.close()
    os.remove(temp_history_db)
    exit(1)

# Przygotuj listy do przechowywania danych
ids = []
urls = []
titles = []
visit_counts = []
last_visit_times = []

# Wyświetl nagłówek ASCII
header = pyfiglet.figlet_format("L C O")
print(header)
time.sleep(2)

# Przetwarzaj wyniki i konwertuj czas
chrome_epoch = datetime(1601, 1, 1)
for res in results:
    id, url, title, visit_count, last_visit_time = res
    # Konwersja czasu Chrome (mikrosekundy od 1601-01-01) na czytelny format
    last_visit_dt = chrome_epoch + timedelta(microseconds=last_visit_time)
    readable_time = last_visit_dt.strftime("%Y-%m-%d %H:%M:%S")

    # Wyświetl dane w konsoli
    print(f"ID: {id}")
    print(f"URL: {url}")
    print(f"Tytuł: {title}")
    print(f"Liczba odwiedzin: {visit_count}")
    print(f"Ostatnia wizyta: {readable_time}")
    print("-" * 50)

    # Dodaj dane do list
    ids.append(id)
    urls.append(url)
    titles.append(title)
    visit_counts.append(visit_count)
    last_visit_times.append(readable_time)

# Zamknij połączenie i usuń tymczasowy plik
c.close()
os.remove(temp_history_db)

