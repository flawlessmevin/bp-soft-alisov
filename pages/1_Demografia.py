import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Demografia mesta Nitra")

st.write("""
Táto sekcia zobrazuje demografické údaje mesta Nitra
na základe dostupných datasetov vo formáte JSON a XLSX.
""")


@st.cache_data
@st.cache_data
def load_demography_data():
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

    return df


@st.cache_data
def load_population_data():
    file_path = "data/demografia/pocety_obcanov_v_jednotlivych_rokoch.xlsx"
    df = pd.read_excel(file_path)

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


def clean_number(x):
    return float(str(x).replace(" ", "").replace(",", "."))


#################################
# DATASET 1: veková štruktúra
#####################################
df = load_demography_data()

#st.write("Počet riadkov po čistení:", len(df))
#st.write("Min vek:", df["vek"].min(), "Max vek:", df["vek"].max())
#st.write("Chýbajúce veky:")

#missing_ages = sorted(set(range(df["vek"].min(), df["vek"].max() + 1)) - set(df["vek"]))
#st.write(missing_ages)

df["vekova_skupina"] = df["vek"].apply(categorize_age)

df_grouped = (
    df.groupby("vekova_skupina")[["pocet_spolu", "muzi", "zeny"]]
    .sum()
    .reset_index()
)

age_order = ["0-14", "15-24", "25-44", "45-64", "65+"]
df_grouped["vekova_skupina"] = pd.Categorical(
    df_grouped["vekova_skupina"],
    categories=age_order,
    ordered=True
)
df_grouped = df_grouped.sort_values("vekova_skupina")

st.header("Veková štruktúra obyvateľstva")

st.subheader("Náhľad datasetu")
st.dataframe(df, use_container_width=True, hide_index=True)



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

st.subheader("Rozdelenie obyvateľov podľa vekových skupín")

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


##################################
# DATASET 2: vývoj populácie
#############################




st.header("Vývoj populácie mesta Nitra")

df_pop = load_population_data()



numeric_cols = [
    "Počet občanov spolu",
    "Počet mužov",
    "Počet žien",
    "Úbytok",
    "Prírastok"
]

for col in numeric_cols:
    df_pop[col] = df_pop[col].apply(clean_number)

df_pop["Rok"] = df_pop["Rok"].astype(int)


df_pop = df_pop.sort_values("Rok")


df_pop["Saldo"] = df_pop["Prírastok"] - df_pop["Úbytok"]
df_pop["Zmena_%"] = df_pop["Počet občanov spolu"].pct_change() * 100

st.subheader("Náhľad datasetu o vývoji populácie")
st.dataframe(df_pop, use_container_width=True, hide_index=True)

st.subheader("Základné ukazovatele vývoja populácie")

col4, col5, col6 = st.columns(3)

with col4:
    st.metric("Posledný evidovaný rok", int(df_pop["Rok"].max()))

with col5:
    st.metric(
        "Počet obyvateľov v poslednom roku",
        int(df_pop.loc[df_pop["Rok"] == df_pop["Rok"].max(), "Počet občanov spolu"].iloc[0])
    )

with col6:
    st.metric(
        "Saldo v poslednom roku",
        int(df_pop.loc[df_pop["Rok"] == df_pop["Rok"].max(), "Saldo"].iloc[0])
    )

st.subheader("Vývoj počtu obyvateľov mesta Nitra")

fig5 = px.line(
    df_pop,
    x="Rok",
    y="Počet občanov spolu",
    labels={"Rok": "Rok", "Počet občanov spolu": "Počet obyvateľov"},
    title="Vývoj počtu obyvateľov mesta Nitra"
)
st.plotly_chart(fig5, use_container_width=True)

st.subheader("Vývoj počtu mužov a žien")

fig6 = px.line(
    df_pop,
    x="Rok",
    y=["Počet mužov", "Počet žien"],
    labels={"Rok": "Rok", "value": "Počet osôb", "variable": "Pohlavie"},
    title="Vývoj počtu mužov a žien"
)
st.plotly_chart(fig6, use_container_width=True)

st.subheader("Demografické saldo")

#df_pop_filtered = df_pop.iloc[3:]
fig7 = px.bar(
    #df_pop_filtered,
    df_pop,
    x="Rok",
    y="Saldo",
    labels={"Rok": "Rok", "Saldo": "Saldo"},
    title="Demografické saldo (prírastok - úbytok)"
)
st.plotly_chart(fig7, use_container_width=True)

st.subheader("Percentuálna zmena populácie")




fig8 = px.line(
    df_pop,
    x="Rok",
    y="Zmena_%",
    labels={"Rok": "Rok", "Zmena_%": "Zmena (%)"},
    title="Percentuálna zmena populácie (%)"
)
st.plotly_chart(fig8, use_container_width=True)



st.subheader("Stručné zhrnutie analýzy")

st.write("""
Na základe spracovaných demografických údajov je možné pozorovať vekovú štruktúru obyvateľstva mesta Nitra,
rozdelenie populácie podľa pohlavia a vývoj počtu obyvateľov v čase.
Vizualizácie umožňujú identifikovať dominantné vekové skupiny, porovnať zastúpenie mužov a žien
a sledovať demografické saldo v jednotlivých rokoch.
Táto časť aplikácie predstavuje základ pre ďalšie rozšírenie analytického dashboardu o ďalšie datasety.
""")