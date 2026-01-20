# ==========================================================
# BDOT10k – AUTOMATYCZNE POBIERANIE I IMPORT WARSTWY BUDYNKÓW
# ==========================================================
# Skrypt:
# - pobiera archiwalne dane BDOT10k z Geoportalu
# - dla lat 2014–2023
# - dla 18 miast wojewódzkich (powiaty – TERYT)
# - rozpakowuje ZIP
# - wyszukuje warstwę BUBD (budynki)
# - importuje ją do geobazy jako: bubd_<rok>_<teryt>
# ==========================================================

import arcpy
import os
import requests # Pobieranie plików z Internetu (HTTP)
import zipfile  # Rozpakowywanie archiwów ZIP
import shutil  # Operacje kopiowania/usuwania plików

# ==========================================================
# KONFIGURACJA
# ==========================================================


# Folder tymczasowy – tutaj trafiają ZIP-y i rozpakowane dane
TEMP_DIR = r"D:\ProjektPPA_dane\temp_bdot10k"
GEOBAZA = r"D:\ProjektPPA_dane\ProjektPPA\ProjektPPA.gdb"

BASE_URL = "https://opendata.geoportal.gov.pl/Archiwum/bdot10k"
LATA = range(2014, 2024)

# województwo : [TERYT powiatu]
MIASTA = {
    "02": ["0264"],           # Wrocław
    "04": ["0461", "0463"],   # Bydgoszcz, Gorzów Wlkp.
    "06": ["0661"],           # Lublin
    "08": ["0861"],           # Zielona Góra
    "10": ["1061"],           # Łódź
    "12": ["1261"],           # Kraków
    "14": ["1465"],           # Warszawa
    "16": ["1661"],           # Opole
    "18": ["1861"],           # Rzeszów
    "20": ["2061"],           # Białystok
    "22": ["2261"],           # Gdańsk
    "24": ["2469"],           # Katowice
    "26": ["2661"],           # Kielce
    "28": ["2861"],           # Olsztyn
    "30": ["3064"],           # Poznań
    "32": ["3262"],           # Szczecin
    "36": ["3661"]            # Toruń
}

arcpy.env.workspace = GEOBAZA
arcpy.env.overwriteOutput = True

# Utworzenie folderu tymczasowego (jeśli nie istnieje)
os.makedirs(TEMP_DIR, exist_ok=True)

# ==========================================================
# FUNKCJE:  POBIERANIE ARCHIWUM ZIP
# ==========================================================

def pobierz_zip(rok, woj, teryt):
    # Składanie pełnego adresu URL
    url = f"{BASE_URL}/{rok}/SHP/{woj}/{teryt}_SHP_{rok}.zip"

     # Lokalna ścieżka zapisu ZIP-a
    zip_path = os.path.join(TEMP_DIR, f"{teryt}_{rok}.zip")


     # Jeśli ZIP już istnieje – nie pobieramy ponownie
    if os.path.exists(zip_path):
        print(f" [ZIP ISTNIEJE] {zip_path}")
        return zip_path

    print(f" [POBIERAM] {url}")
    r = requests.get(url, stream=True)

    # Jeśli serwer nie zwrócił 200 – dane nie istnieją
    if r.status_code != 200:
        print(f" [BRAK DANYCH] {url}")
        return None

       # Zapis pliku ZIP na dysku
    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

    return zip_path


 #    Rozpakowuje archiwum ZIP do folderu o tej samej nazwie
def rozpakuj_zip(zip_path):
    folder = zip_path.replace(".zip", "")

     # Rozpakowanie tylko jeśli folder jeszcze nie istnieje
    if not os.path.exists(folder):
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(folder)
    return folder


# ==========================================================
# FUNKCJA: WYSZUKIWANIE WARSTWY BUBD
# ==========================================================


# Przeszukuje strukturę katalogów BDOT10k
    #i zwraca ścieżkę do pliku SHP z budynkami (BUBD)
def znajdz_bubd(folder):
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".shp") and "bubd" in f.lower():
                return os.path.join(root, f)
    return None


# ==========================================================
# FUNKCJA: IMPORT DO GEOBAZY
# ==========================================================

# Importuje warstwę BUBD do geobazy jako: bubd_<rok>_<teryt>

def importuj_bubd(shp_path, rok, teryt):
    nazwa = f"bubd_{rok}_{teryt}"

    if arcpy.Exists(nazwa):
        print(f"  [POMINIĘTO] {nazwa} już istnieje")
        return

    arcpy.conversion.ExportFeatures(shp_path, nazwa)
    print(f"  [ZAIMPORTOWANO] {nazwa}")


# ==========================================================
# GŁÓWNA PĘTLA
# ==========================================================

print("\n=== START BDOT10k ===")

for rok in LATA:
    print(f"\n--- ROK {rok} ---")
    for woj, teryty in MIASTA.items():
        for teryt in teryty:
            zip_path = pobierz_zip(rok, woj, teryt)
            if not zip_path:
                continue

            folder = rozpakuj_zip(zip_path)
            bubd = znajdz_bubd(folder)

            if bubd:
                importuj_bubd(bubd, rok, teryt)
            else:
                print(f"  [BRAK BUBD] {teryt} {rok}")

print("\n=== KONIEC SKRYPTU ===")
