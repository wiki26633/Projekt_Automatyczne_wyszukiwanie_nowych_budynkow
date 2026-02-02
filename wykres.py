import arcpy
import matplotlib.pyplot as plt
import os


GEOBAZA = r"D:\ProjektPPA_dane\ProjektPPA\ProjektPPA.gdb"
arcpy.env.workspace = GEOBAZA
arcpy.env.overwriteOutput = True

output_dir = r"D:\ProjektPPA\wykresy"
os.makedirs(output_dir, exist_ok=True) 

sciezka = os.path.join(output_dir, "budynki_calkowite_miasta.jpg")


MIASTA = {
    "02": {"0264": "Wrocław"},
    "04": {"0461": "Bydgoszcz", "0463": "Toruń"},
    "06": {"0663": "Lublin"},
    "08": {"0861": "Gorzów Wlkp.", "0862": "Zielona Góra"},
    "10": {"1061": "Łódź"},
    "12": {"1261": "Kraków"},
    "14": {"1465": "Warszawa"},
    "16": {"1661": "Opole"},
    "18": {"1863": "Rzeszów"},
    "20": {"2061": "Białystok"},
    "22": {"2261": "Gdańsk"},
    "24": {"2469": "Katowice"},
    "26": {"2661": "Kielce"},
    "28": {"2862": "Olsztyn"},
    "30": {"3064": "Poznań"},
    "32": {"3262": "Szczecin"}
}

LATA = list(range(2014, 2024))


liczba_budynkow_miast = {}

for woj, teryty_dict in MIASTA.items():
    for teryt, nazwa_miasta in teryty_dict.items():
        total = 0
        for rok in LATA:
            fc_name = f"bubd_{rok}_{teryt}"
            if arcpy.Exists(fc_name):
                count = int(arcpy.management.GetCount(fc_name)[0])
                total += count
        liczba_budynkow_miast[nazwa_miasta] = total


miasta_labels = list(liczba_budynkow_miast.keys())
wartosci = list(liczba_budynkow_miast.values())

plt.figure(figsize=(15, 7))
bars = plt.bar(miasta_labels, wartosci, color='skyblue', edgecolor='navy')
plt.xlabel("Miasto", fontsize=12)
plt.ylabel("Całkowita liczba nowych budynków (2014-2023)", fontsize=12)
plt.title("Łączna liczba nowych budynków w miastach wojewódzkich (2014-2023)", fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)


for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 100, str(height), ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(sciezka, dpi=300, bbox_inches='tight', format='jpg')
plt.close()
print(f"Wykres zapisany do: {sciezka}")
