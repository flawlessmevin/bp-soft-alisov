import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Demografia mesta Nitra")

st.write("""
Táto sekcia zobrazuje vekovú štruktúru obyvateľov mesta Nitra
na základe dostupného datasetu vo formáte JSON.
""")


@st.cache_data
def load_demography_data():
    file_path = "data/pocet_obcanov_podla_veku_DATA.json"
    df = pd.read_json(file_path)

    # Premenovanie stĺpcov na jednoduchšie názvy
    df = df.rename(columns={
        "Vek": "vek",
        "Počet_občanov_v_danom_veku": "pocet_spolu",
        "Počet_mužov": "muzi",
        "Počet_žien": "zeny"
    })

    # Odstránenie medzier a prevod na čísla
    df["vek"] = pd.to_numeric(df["vek"].astype(str).str.strip(), errors="coerce")
    df["pocet_spolu"] = pd.to_numeric(df["pocet_spolu"].astype(str).str.strip(), errors="coerce")
    df["muzi"] = pd.to_numeric(df["muzi"].astype(str).str.strip(), errors="coerce")
    df["zeny"] = pd.to_numeric(df["zeny"].astype(str).str.strip(), errors="coerce")

    # Odstránenie riadkov s chýbajúcimi hodnotami
    df = df.dropna()

    # Prevod na int
    df["vek"] = df["vek"].astype(int)
    df["pocet_spolu"] = df["pocet_spolu"].astype(int)
    df["muzi"] = df["muzi"].astype(int)
    df["zeny"] = df["zeny"].astype(int)

    return df


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


# Načítanie dát
df = load_demography_data()

# Vytvorenie vekových skupín
df["vekova_skupina"] = df["vek"].apply(categorize_age)

df_grouped = (
    df.groupby("vekova_skupina")[["pocet_spolu", "muzi", "zeny"]]
    .sum()
    .reset_index()
)

# Nastavenie správneho poradia vekových skupín
age_order = ["0-14", "15-24", "25-44", "45-64", "65+"]
df_grouped["vekova_skupina"] = pd.Categorical(
    df_grouped["vekova_skupina"],
    categories=age_order,
    ordered=True
)
df_grouped = df_grouped.sort_values("vekova_skupina")


st.subheader("Náhľad datasetu")
st.dataframe(df, use_container_width=True)

st.subheader("Základné štatistiky")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Celkový počet záznamov", len(df))

with col2:
    st.metric("Súčet obyvateľov", int(df["pocet_spolu"].sum()))

with col3:
    st.metric("Najvyšší evidovaný vek", int(df["vek"].max()))

st.subheader("Počet obyvateľov podľa veku")

fig1 = px.bar(
    df,
    x="vek",
    y="pocet_spolu",
    labels={"vek": "Vek", "pocet_spolu": "Počet obyvateľov"},
    title="Počet obyvateľov podľa veku"
)

st.plotly_chart(fig1, use_container_width=True)

st.subheader("Porovnanie mužov a žien podľa veku")

df_gender = df.melt(
    id_vars="vek",
    value_vars=["muzi", "zeny"],
    var_name="pohlavie",
    value_name="pocet"
)

fig2 = px.line(
    df_gender,
    x="vek",
    y="pocet",
    color="pohlavie",
    labels={"vek": "Vek", "pocet": "Počet osôb", "pohlavie": "Pohlavie"},
    title="Porovnanie mužov a žien podľa veku"
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("Veková štruktúra obyvateľstva")

fig3 = px.bar(
    df_grouped,
    x="vekova_skupina",
    y="pocet_spolu",
    labels={"vekova_skupina": "Veková skupina", "pocet_spolu": "Počet obyvateľov"},
    title="Rozdelenie obyvateľov podľa vekových skupín"
)

st.plotly_chart(fig3, use_container_width=True)

st.subheader("Porovnanie mužov a žien podľa vekových skupín")

fig4 = px.bar(
    df_grouped,
    x="vekova_skupina",
    y=["muzi", "zeny"],
    barmode="group",
    labels={
        "vekova_skupina": "Veková skupina",
        "value": "Počet osôb",
        "variable": "Pohlavie"
    },
    title="Porovnanie mužov a žien podľa vekových skupín"
)

st.plotly_chart(fig4, use_container_width=True)