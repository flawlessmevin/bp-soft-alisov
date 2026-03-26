import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Demografia mesta Nitra")

st.write("""
Táto sekcia zobrazuje demografické údaje mesta Nitra
na základe dostupných datasetov vo formáte JSON a XLSX.
""")


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

def reset_filters():
    st.session_state["age_range"] = (min_age, max_age)
    st.session_state["gender_view"] = "Spolu"
    st.session_state["year_range"] = (min_year, max_year)


# =============================
# LOAD DATA
# =============================
df = load_demography_data()
df["vekova_skupina"] = df["vek"].apply(categorize_age)

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
df_pop = df_pop.sort_values("Rok").reset_index(drop=True)
df_pop["Saldo"] = df_pop["Prírastok"] - df_pop["Úbytok"]
df_pop["Zmena_%"] = df_pop["Počet občanov spolu"].pct_change() * 100


# =============================
# SIDEBAR
# =============================
st.sidebar.header("Filtre stránky")

st.sidebar.subheader("Veková štruktúra")

min_age = int(df["vek"].min())
max_age = int(df["vek"].max())

selected_age_range = st.sidebar.slider(
    "Vekový rozsah",
    min_age,
    max_age,
    (min_age, max_age),
    key="age_range"
)

selected_gender_view = st.sidebar.selectbox(
    "Zobrazenie",
    ["Spolu", "Muži", "Ženy"],
    key= "gender_view"
)



st.sidebar.subheader("Vývoj populácie")

min_year = int(df_pop["Rok"].min())
max_year = int(df_pop["Rok"].max())

selected_year_range = st.sidebar.slider(
    "Rozsah rokov",
    min_year,
    max_year,
    (min_year, max_year),
    key= "year_range"
)

st.sidebar.markdown("---")
st.sidebar.button("🔄 Resetovať filtre", on_click=reset_filters)



# =============================
# FILTERED DATA
# =============================
df_filtered = df[
    (df["vek"] >= selected_age_range[0]) &
    (df["vek"] <= selected_age_range[1])
].copy()

df_grouped_filtered = (
    df_filtered.groupby("vekova_skupina")[["pocet_spolu", "muzi", "zeny"]]
    .sum()
    .reset_index()
)

age_order = ["0-14", "15-24", "25-44", "45-64", "65+"]
df_grouped_filtered["vekova_skupina"] = pd.Categorical(
    df_grouped_filtered["vekova_skupina"],
    categories=age_order,
    ordered=True
)
df_grouped_filtered = df_grouped_filtered.sort_values("vekova_skupina")

df_pop_filtered = df_pop[
    (df_pop["Rok"] >= selected_year_range[0]) &
    (df_pop["Rok"] <= selected_year_range[1])
].copy()


# =============================
# DISPLAY SETTINGS
# =============================
y_column = "pocet_spolu"
y_label = "Počet obyvateľov"

if selected_gender_view == "Muži":
    y_column = "muzi"
    y_label = "Počet mužov"
elif selected_gender_view == "Ženy":
    y_column = "zeny"
    y_label = "Počet žien"


# =============================
# TABS
# =============================
tab1, tab2, tab3 = st.tabs([
    "Prehľad",
    "Veková štruktúra",
    "Vývoj populácie"
])


# =============================
# TAB 1 - PREHĽAD
# =============================
with tab1:
    st.header("Rýchly prehľad")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Počet vekových záznamov", len(df_filtered))

    with col2:
        st.metric("Súčet v zvolenom rozsahu", int(df_filtered[y_column].sum()))

    with col3:
        st.metric("Posledný evidovaný rok", int(df_pop_filtered["Rok"].max()))

    with col4:
        latest_year = df_pop_filtered["Rok"].max()
        latest_population = int(
            df_pop_filtered.loc[
                df_pop_filtered["Rok"] == latest_year,
                "Počet občanov spolu"
            ].iloc[0]
        )
        st.metric("Počet obyvateľov v poslednom roku", latest_population)

    st.subheader("Hlavný graf vekovej štruktúry")


    fig_overview = px.line(
        df_filtered,
        x="vek",
        y=y_column,
        labels={"vek": "Vek", y_column: y_label},
        title=f"{y_label} podľa veku"
    )

    st.plotly_chart(fig_overview, use_container_width=True, key="overview_chart")

    st.subheader("Stručné zhrnutie")

    if len(df_filtered) > 0:
        top_age_row = df_filtered.loc[df_filtered[y_column].idxmax()]
        st.write(
            f"V zvolenom vekovom rozsahu sa najvyššia hodnota nachádza pri veku "
            f"**{int(top_age_row['vek'])}**, kde bolo evidovaných **{int(top_age_row[y_column])}** osôb."
        )

    latest_saldo = int(
        df_pop_filtered.loc[
            df_pop_filtered["Rok"] == latest_year,
            "Saldo"
        ].iloc[0]
    )

    st.write(
        f"V poslednom dostupnom roku **{latest_year}** bol zaznamenaný celkový počet "
        f"**{latest_population}** obyvateľov a demografické saldo dosiahlo hodnotu "
        f"**{latest_saldo}**."
    )


# =============================
# TAB 2 - VEKOVÁ ŠTRUKTÚRA
# =============================
with tab2:
    st.header("Veková štruktúra obyvateľstva")

    st.subheader(f"{y_label} podľa veku")

    fig1 = px.line(
        df_filtered,
        x="vek",
        y=y_column,
        labels={"vek": "Vek", y_column: y_label},
        title=f"{y_label} podľa veku"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Porovnanie mužov a žien podľa veku")

    df_gender = df_filtered.melt(
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
    st.plotly_chart(fig2, use_container_width=True, key="gender_chart")

    st.subheader("Rozdelenie obyvateľov podľa vekových skupín")

    fig3 = px.bar(
        df_grouped_filtered,
        x="vekova_skupina",
        y="pocet_spolu",
        labels={"vekova_skupina": "Veková skupina", "pocet_spolu": "Počet obyvateľov"},
        title="Rozdelenie obyvateľov podľa vekových skupín"
    )
    st.plotly_chart(fig3, use_container_width=True, key="group_chart")

    st.subheader("Porovnanie mužov a žien podľa vekových skupín")

    fig4 = px.bar(
        df_grouped_filtered,
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
    st.plotly_chart(fig4, use_container_width=True, key="group_gender_chart")


# =============================
# TAB 3 - VÝVOJ POPULÁCIE
# =============================
with tab3:
    st.header("Vývoj populácie mesta Nitra")

    st.subheader("Základné ukazovatele vývoja populácie")

    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric("Počiatočný rok", int(df_pop_filtered["Rok"].min()))

    with col6:
        st.metric("Posledný rok", int(df_pop_filtered["Rok"].max()))

    with col7:
        latest_year_tab3 = df_pop_filtered["Rok"].max()
        latest_saldo_tab3 = int(
            df_pop_filtered.loc[
                df_pop_filtered["Rok"] == latest_year_tab3,
                "Saldo"
            ].iloc[0]
        )
        st.metric("Saldo v poslednom roku", latest_saldo_tab3)

    st.subheader("Vývoj počtu obyvateľov mesta Nitra")

    fig5 = px.line(
        df_pop_filtered,
        x="Rok",
        y="Počet občanov spolu",
        labels={"Rok": "Rok", "Počet občanov spolu": "Počet obyvateľov"},
        title="Vývoj počtu obyvateľov mesta Nitra"
    )
    st.plotly_chart(fig5, use_container_width=True, key="pop_total")

    st.subheader("Vývoj počtu mužov a žien")

    fig6 = px.line(
        df_pop_filtered,
        x="Rok",
        y=["Počet mužov", "Počet žien"],
        labels={"Rok": "Rok", "value": "Počet osôb", "variable": "Pohlavie"},
        title="Vývoj počtu mužov a žien"
    )
    st.plotly_chart(fig6, use_container_width=True, key="pop_gender")

    st.subheader("Demografické saldo")

    fig7 = px.bar(
        df_pop_filtered[df_pop_filtered["Rok"] != df_pop_filtered["Rok"].min()],
        x="Rok",
        y="Saldo",
        labels={"Rok": "Rok", "Saldo": "Saldo"},
        title="Demografické saldo (prírastok - úbytok)"
    )
    st.plotly_chart(fig7, use_container_width=True, key="pop_saldo")

    st.subheader("Percentuálna zmena populácie")

    fig8 = px.line(
        df_pop_filtered[df_pop_filtered["Rok"] != df_pop_filtered["Rok"].min()],
        x="Rok",
        y="Zmena_%",
        labels={"Rok": "Rok", "Zmena_%": "Zmena (%)"},
        title="Percentuálna zmena populácie (%)"
    )
    st.plotly_chart(fig8, use_container_width=True, key="pop_change")


