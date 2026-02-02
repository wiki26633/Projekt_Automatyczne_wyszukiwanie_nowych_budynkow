# BDOT10k – AUTOMATYCZNE POBIERANIE I IMPORT WARSTWY BUDYNKÓW
# Skrypt:
# - pobiera archiwalne dane BDOT10k z Geoportalu
# - dla lat 2014–2023
# - dla 18 miast wojewódzkich (powiaty – TERYT)
# - rozpakowuje ZIP
# - wyszukuje warstwę BUBD (budynki)
# - importuje ją do geobazy

import arcpy
import os
import requests
import zipfile
import shutil

# ==========================================================
# KONFIGURACJA
# ==========================================================

TEMP_DIR = r"D:\ProjektPPA_dane\temp_bdot10k"
GEOBAZA = r"D:\ProjektPPA_dane\ProjektPPA\ProjektPPA.gdb"
BASE_URL = "https://opendata.geoportal.gov.pl/Archiwum/bdot10k"
LATA = range(2014, 2024)

MIASTA = {
    "02": ["0264"],          # Wrocław
    "04": ["0461", "0463"],  # Bydgoszcz, Toruń
    "06": ["0663"],          # Lublin
    "08": ["0861", "0862"],  # Gorzów Wlkp.,  Zielona Góra
    "10": ["1061"],          # Łódź
    "12": ["1261"],          # Kraków
    "14": ["1465"],          # Warszawa
    "16": ["1661"],          # Opole
    "18": ["1863"],          # Rzeszów
    "20": ["2061"],          # Białystok
    "22": ["2261"],          # Gdańsk 
    "24": ["2469"],          # Katowice
    "26": ["2661"],          # Kielce
    "28": ["2862"],          # Olsztyn
    "30": ["3064"],          # Poznań 
    "32": ["3262"]           # Szczecin
}

arcpy.env.workspace = GEOBAZA
arcpy.env.overwriteOutput = True
os.makedirs(TEMP_DIR, exist_ok=True)

# ==========================================================
# FUNKCJE
# ==========================================================

def pobierz_zip(rok, woj, teryt):
    url = f"{BASE_URL}/{rok}/SHP/{woj}/{teryt}_SHP_{rok}.zip"
    zip_path = os.path.join(TEMP_DIR, f"{teryt}_{rok}.zip")
    if os.path.exists(zip_path):
        return zip_path
    print(f" [POBIERAM] {url}")
    try:
        r = requests.get(url, stream=True, timeout=60)
        if r.status_code != 200:
            return None
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return zip_path
    except:
        return None

def rozpakuj_zip(zip_path):
    folder = zip_path.replace(".zip", "")
    if not os.path.exists(folder):
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(folder)
        except:
            return None
    return folder

def przygotuj_czysty_shp(folder_search, teryt, rok):
    """Znajduje BUBD i kopiuje go pod prostą nazwą do osobnego folderu."""
    target_shp = None
    for root, dirs, files in os.walk(folder_search):
        for f in files:
            if f.lower().endswith(".shp") and "bubd" in f.lower():
                target_shp = os.path.join(root, f)
                break
        if target_shp: break

    if not target_shp:
        return None

    # Tworzymy folder 'clean', aby uniknąć konfliktów z kropkami w nazwach
    clean_dir = os.path.join(TEMP_DIR, f"clean_{teryt}_{rok}")
    if os.path.exists(clean_dir): shutil.rmtree(clean_dir)
    os.makedirs(clean_dir)

    # Nowa, prosta nazwa bez kropek 
    nowa_bazowa_nazwa = "BUBD_TEMP"
    stara_bazowa_nazwa = os.path.splitext(os.path.basename(target_shp))[0]
    folder_zrodlowy = os.path.dirname(target_shp)

    # Kopiujemy komplet plików składowych
    rozszerzenia = ['.shp', '.shx', '.dbf', '.prj', '.cpg']
    for ext in rozszerzenia:
        plik_src = os.path.join(folder_zrodlowy, stara_bazowa_nazwa + ext)
        plik_dst = os.path.join(clean_dir, nowa_bazowa_nazwa + ext)
        if os.path.exists(plik_src):
            shutil.copy2(plik_src, plik_dst)

    return os.path.join(clean_dir, nowa_bazowa_nazwa + ".shp")

def importuj(shp_path, rok, teryt):
    cel = f"bubd_{rok}_{teryt}"
    if arcpy.Exists(cel):
        print(f"  [POMINIĘTO] {cel}")
        return
    try:
        arcpy.conversion.ExportFeatures(shp_path, cel)
        print(f"  [OK] Zaimportowano {cel}")
    except Exception as e:
        print(f"  [BŁĄD] {cel}: {e}")

# ==========================================================
# URUCHOMIENIE
# ==========================================================

print("=== START BDOT10k ===")
for rok in LATA:
    for woj, teryty in MIASTA.items():
        for teryt in teryty:
            zip_p = pobierz_zip(rok, woj, teryt)
            if not zip_p: continue
            
            f_data = rozpakuj_zip(zip_p)
            if not f_data: continue

            # Naprawa struktury i nazw
            czysty_shp = przygotuj_czysty_shp(f_data, teryt, rok)
            
            if czysty_shp:
                importuj(czysty_shp, rok, teryt)
                # Opcjonalnie: usuń folder clean po imporcie
                # shutil.rmtree(os.path.dirname(czysty_shp))
            else:
                print(f"  [BRAK BUBD] {teryt} {rok}")

print("===  KONIEC  ===")