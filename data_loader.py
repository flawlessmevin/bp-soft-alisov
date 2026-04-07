import pandas as pd
import requests
from io import BytesIO


def clean_number(x):
    return float(str(x).replace(" ", "").replace(",", "."))


# =============================
# DEMOGRAFIA
# =============================


def load_age_data():
    file_path = "data/demografia/pocet_obcanov_podla_veku_DATA.json"
    df = pd.read_json(file_path)

    df = df.rename(columns={
        "Vek": "vek",
        "Počet_občanov_v_danom_veku": "pocet_spolu",
        "Počet_mužov": "muzi",
        "Počet_žien": "zeny"
    })

    def clean_numeric(series):
        return pd.to_numeric(
            series.astype(str)
            .str.replace(r"[^\d,.\-]", "", regex=True)
            .str.replace(",", ".", regex=False),
            errors="coerce"
        )

    def categorize_age(age):
        if age <= 14:
            return "0-14"
        elif age <= 24:
            return "15-24"
        elif age <= 44:
            return "25-44"
        elif age <= 64:
            return "45-64"
        else:
            return "65+"

    df["vek"] = clean_numeric(df["vek"])
    df["pocet_spolu"] = clean_numeric(df["pocet_spolu"])
    df["muzi"] = clean_numeric(df["muzi"])
    df["zeny"] = clean_numeric(df["zeny"])

    df = df.dropna(subset=["vek"])

    df["pocet_spolu"] = df["pocet_spolu"].fillna(0)
    df["muzi"] = df["muzi"].fillna(0)
    df["zeny"] = df["zeny"].fillna(0)

    df["vek"] = df["vek"].astype(int)
    df["pocet_spolu"] = df["pocet_spolu"].astype(int)
    df["muzi"] = df["muzi"].astype(int)
    df["zeny"] = df["zeny"].astype(int)

    df = df.sort_values("vek").reset_index(drop=True)
    df["vekova_skupina"] = df["vek"].apply(categorize_age)
    return df
#######################################


def load_street_data():
    file_path = "data/demografia/pocet_obcanov_podla_ulic.json"
    df = pd.read_json(file_path)

    df = df.rename(columns={
        "Ulica": "ulica",
        "Na_trvalom_pobyte": "trvaly_pobyt",
        "Na_prechodnom_pobyte": "prechodny_pobyt",
        "Ženy": "zeny",
        "Muži": "muzi",
        "V_predproduktívnom_veku": "predproduktivny",
        "V_produktívnom_veku": "produktivny",
        "V_poproduktívnom_veku": "poproduktivny"
    })

    def clean_numeric(series):
        return pd.to_numeric(
            series.astype(str)
            .str.replace(r"[^\d,.\-]", "", regex=True)
            .str.replace(",", ".", regex=False),
            errors="coerce"
        )

    numeric_cols = [
        "trvaly_pobyt",
        "prechodny_pobyt",
        "zeny",
        "muzi",
        "predproduktivny",
        "produktivny",
        "poproduktivny"
    ]

    for col in numeric_cols:
        df[col] = clean_numeric(df[col]).fillna(0).astype(int)

    df["spolu"] = df["trvaly_pobyt"] + df["prechodny_pobyt"]


    df = df[df["ulica"] != "* mesto Nitra"].copy()

    df = df.sort_values("spolu", ascending=False).reset_index(drop=True)
    return df
################################

def load_population_data():
    file_path = "data/demografia/pocety_obcanov_v_jednotlivych_rokoch.xlsx"
    df = pd.read_excel(file_path)

    df["Rok"] = df["Rok"].astype(int)
    df = df.sort_values("Rok").reset_index(drop=True)
    df["Saldo"] = df["Prírastok"] - df["Úbytok"]
    df["Zmena_%"] = df["Počet občanov spolu"].pct_change() * 100



    numeric_cols = [
        "Počet občanov spolu",
        "Počet mužov",
        "Počet žien",
        "Úbytok",
        "Prírastok"
    ]

    for col in numeric_cols:
        df[col] = df[col].apply(clean_number)


    return df













# =============================
# ROZPOCET
# =============================


def load_budget_data():
    file_path = "data/rozpocet/Rozpocet.xlsx"
    df = pd.read_excel(file_path)



    df["Príjmy"] = df["Príjmy"].apply(clean_number)
    df["Výdavky"] = df["Výdavky"].apply(clean_number)
    df["Rozdiel"] = df["Rozdiel"].apply(clean_number)
    df["Rok"] = df["Rok"].astype(int)

    df = df.sort_values("Rok").reset_index(drop=True)

    df["Efektivita"] = df["Príjmy"] / df["Výdavky"]
    df["Príjmy_change_%"] = df["Príjmy"].pct_change() * 100
    df["Výdavky_change_%"] = df["Výdavky"].pct_change() * 100


    return df



def load_debtors_data():
    df = pd.read_json("data/rozpocet/Zoznam_Zoznam_daňových_dlžníkov.json")

    df = df.rename(columns={
        "Dlžník": "dlznik",
        "Adresa_dlžníka": "adresa",
        "Mesto": "mesto",
        "Suma_daňových_nedoplatkov_k_31.12._predch._roka": "nedoplatok_minuly",
        "Suma_daňových_nedoplatkov": "nedoplatok",
        "Mena": "mena"
    })

    df["nedoplatok"] = df["nedoplatok"].apply(clean_number)
    df["nedoplatok_minuly"] = df["nedoplatok_minuly"].apply(clean_number)

    return df



def load_orders_data():
    df = pd.read_json("data/rozpocet/Zoznam_Dodávateľské_faktúry.json")

    df = df.rename(columns={
        "Číslo_faktúry": "cislo_faktury",
        "Dodávateľ": "dodavatel",
        "Predmet_faktúry": "predmet",
        "Celková_cena": "cena",
        "Mena": "mena",
        "Dátum_vystavenia": "datum_vystavenia",
        "Dátum_zverejnenia": "datum_zverejnenia",
        "IČO": "ico"
    })

    df["cena"] = df["cena"].apply(clean_number)
    df["datum_vystavenia"] = pd.to_datetime(
        df["datum_vystavenia"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    df["rok"] = df["datum_vystavenia"].dt.year

    return df

