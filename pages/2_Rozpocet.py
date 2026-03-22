import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Rozpočet mesta Nitra")

st.write("""
Táto sekcia zobrazuje analýzu rozpočtu mesta Nitra.
""")


@st.cache_data
def load_budget_data():
    file_path = "data/Rozpocet.xlsx"
    df = pd.read_excel(file_path)

    return df


df = load_budget_data()

st.subheader("Náhľad datasetu")
st.dataframe(df, use_container_width=True)


fig1 = px.line(
    df,
    x="Rok",
    y=["Príjmy", "Výdavky"],
    title="Vývoj príjmov a výdavkov mesta v čase"
)

st.plotly_chart(fig1, use_container_width=True)


fig2 = px.bar(
    df,
    x="Rok",
    y="Rozdiel",
    title="Rozdiel medzi príjmami a výdavkami"
)

st.plotly_chart(fig2, use_container_width=True)


df_melt = df.melt(
    id_vars="Rok",
    value_vars=["Príjmy", "Výdavky"],
    var_name="Typ",
    value_name="Hodnota"
)

fig3 = px.bar(
    df_melt,
    x="Rok",
    y="Hodnota",
    color="Typ",
    barmode="group",
    title="Porovnanie príjmov a výdavkov"
)

st.plotly_chart(fig3, use_container_width=True)



df["Efektivita"] = df["Príjmy"] / df["Výdavky"]

fig4 = px.line(
    df,
    x="Rok",
    y="Efektivita",
    title="Efektivita hospodárenia mesta"
)

st.plotly_chart(fig4, use_container_width=True)



df["Príjmy_change_%"] = df["Príjmy"].pct_change() * 100

fig5 = px.line(
    df,
    x="Rok",
    y="Príjmy_change_%",
    title="Percentuálna zmena príjmov (%)"
)

st.plotly_chart(fig5, use_container_width=True)



def clean_number(x):
    return float(str(x).replace(" ", "").replace(",", "."))

df["Príjmy"] = df["Príjmy"].apply(clean_number)
df["Výdavky"] = df["Výdavky"].apply(clean_number)
df["Rozdiel"] = df["Rozdiel"].apply(clean_number)