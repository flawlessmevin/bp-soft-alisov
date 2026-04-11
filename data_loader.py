import pandas as pd
import requests
from io import BytesIO

from pathlib import Path
import streamlit as st



def _download_json_bytes(url: str, timeout: int = 20) -> bytes:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.content


@st.cache_data(show_spinner=False, ttl=3600)
def load_json_with_fallback(url: str, local_path: str) -> pd.DataFrame:
    local_file = Path(local_path)
    local_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        content = _download_json_bytes(url)
        df = pd.read_json(io.BytesIO(content))
        local_file.write_bytes(content)
        return df

    except Exception:
        if local_file.exists():
            return pd.read_json(local_file)
        raise





def clean_number(x):
    return float(str(x).replace(" ", "").replace(",", "."))


# =============================
# DEMOGRAFIA
# =============================


def load_age_data():
    url = "https://klient.nitra.sk/Default.aspx?NavigationState=920:0::plac1140:_144053_5_8"
    local_path = "data/demografia/pocet_obcanov_podla_veku_DATA.json"
    df = load_json_with_fallback(url, local_path)

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
    url = "https://klient.nitra.sk/Default.aspx?NavigationState=900:0::plac520:_144017_5_8"
    local_path = "data/demografia/pocet_obcanov_podla_ulic.json"
    df = load_json_with_fallback(url, local_path)

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
    url = "https://klient.nitra.sk/Default.aspx?NavigationState=880:0::plac2009:_144107_5_8"
    local_path = "data/demografia/Zoznam_Počty_občanov_v_jednotlivých_rokoch.json"
    df = load_json_with_fallback(url, local_path)

    df = df.rename(columns={
        "Počet_občanov_spolu": "Počet občanov spolu",
        "Počet_mužov": "Počet mužov",
        "Počet_žien": "Počet žien",
        "Úbytok": "Úbytok",
        "Prírastok": "Prírastok"
    })

    numeric_cols = [
        "Počet občanov spolu",
        "Počet mužov",
        "Počet žien",
        "Úbytok",
        "Prírastok"
    ]

    for col in numeric_cols:
        df[col] = df[col].apply(clean_number)

    df["Rok"] = pd.to_numeric(df["Rok"], errors="coerce")
    df = df.dropna(subset=["Rok"]).copy()
    df["Rok"] = df["Rok"].astype(int)

    df = df.sort_values("Rok").reset_index(drop=True)

    df["Saldo"] = df["Prírastok"] - df["Úbytok"]
    df["Zmena_%"] = df["Počet občanov spolu"].pct_change() * 100

    return df











# =============================
# ROZPOCET
# =============================


def load_budget_data():
    url = "https://klient.nitra.sk/Default.aspx?NavigationState=440:0::plac1989:_144106_5_8"
    local_path = "data/rozpocet/Zoznam_Rozdiel_príjmov_a_výdavkov_rozpočtov_po_rokoch.json"
    df = load_json_with_fallback(url, local_path)



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
    url = "https://klient.nitra.sk/Default.aspx?NavigationState=806:0::plac2117:_272003_5_8"
    local_path = "data/rozpocet/Zoznam_Zoznam_daňových_dlžníkov.json"
    df = load_json_with_fallback(url, local_path)

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
    url = "https://klient.nitra.sk/Default.aspx?NavigationState=781:0::plac1931:_144104_5_8"
    local_path = "data/rozpocet/Zoznam_Dodávateľské_faktúry.json"

    df = load_json_with_fallback(url, local_path)

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

    

