import arcpy
import os

# ==========================================================
# KONFIGURACJA
# ==========================================================

GEOBAZA = r"D:\ProjektPPA_dane\ProjektPPA\ProjektPPA.gdb"
arcpy.env.workspace = GEOBAZA
arcpy.env.overwriteOutput = True


MIASTA = {
    "02": ["0264"],           # Wrocław
    "04": ["0461", "0463"],   # Bydgoszcz, Toruń
    "06": ["0663"],           # Lublin
    "08": ["0861", "0862"],   # Gorzów Wlkp., Zielona Góra
    "10": ["1061"],           # Łódź
    "12": ["1261"],           # Kraków
    "14": ["1465"],           # Warszawa
    "16": ["1661"],           # Opole
    "18": ["1863"],           # Rzeszów
    "20": ["2061"],           # Białystok
    "22": ["2261"],           # Gdańsk
    "24": ["2469"],           # Katowice
    "26": ["2661"],           # Kielce
    "28": ["2862"],           # Olsztyn
    "30": ["3064"],           # Poznań
    "32": ["3262"]            # Szczecin
}

LATA = list(range(2014, 2024))


def wybierz_nowe_budynki(poprzednie_budynki, aktualne_budynki, wyjscie_fc):
    """
    Tworzy feature class nowych budynków w aktualne_budynki w stosunku do poprzedniego roku.
    Jeśli brak danych z poprzedniego roku, nic nie robi.
    """
    if not poprzednie_budynki:
        # Brak danych z poprzedniego roku = nic nie robimy
        print(f"  [POMINIĘTO] brak danych z poprzedniego roku, rok pominięty")
        return
    
    warstwa_tymczasowa = "warstwa_tymczasowa"
    arcpy.management.MakeFeatureLayer(aktualne_budynki, warstwa_tymczasowa)
    
    # Select By Location - wybieramy budynki, które nie istnieją w poprzednim roku
    arcpy.management.SelectLayerByLocation(
        warstwa_tymczasowa,
        "INTERSECT",
        poprzednie_budynki,
        selection_type="NEW_SELECTION",
        invert_spatial_relationship="INVERT"
    )
    
    
    arcpy.management.CopyFeatures(warstwa_tymczasowa, wyjscie_fc)
    print(f"  [OK] {wyjscie_fc} - nowe budynki")



print("=== START ANALIZY NOWYCH BUDYNKÓW ===")

poprzednie_budynki = None

for rok in LATA:
    print(f"\n--- ROK {rok} ---")
    
    # Zbieramy wszystkie budynki z miast wojewódzkich dla roku
    miasta_fc = []
    for woj, teryty in MIASTA.items():
        for teryt in teryty:
            fc_name = f"bubd_{rok}_{teryt}"
            if arcpy.Exists(fc_name):
                miasta_fc.append(fc_name)
    
    if not miasta_fc:
        print(f"  [BRAK DANYCH] rok {rok}")
        poprzednie_budynki = None
        continue
    
    # Scalanie wszystkich miast wojewódzkich w jedena warstwę
    if len(miasta_fc) > 1:
        aktualne_budynki = f"bubd_miasta_{rok}"
        arcpy.management.Merge(miasta_fc, aktualne_budynki)
    else:
        aktualne_budynki = miasta_fc[0]
    
    # Tworzymy warstwę nowych budynków tylko jeśli poprzedni rok istnieje
    nowebudynki_fc = f"bubd_miasta_new_{rok}"
    wybierz_nowe_budynki(poprzednie_budynki, aktualne_budynki, nowebudynki_fc)
    
   
    poprzednie_budynki = aktualne_budynki

print("\n=== KONIEC ANALIZY ===")
