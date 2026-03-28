import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Rozpočet mesta Nitra")

st.write("""
Táto sekcia zobrazuje analýzu rozpočtových údajov mesta Nitra.
""")


@st.cache_data
def load_budget_data():
    file_path = "data/Rozpocet.xlsx"
    df = pd.read_excel(file_path)
    return df


def clean_number(x):
    return float(str(x).replace(" ", "").replace(",", "."))


# =============================
# LOAD + CLEAN DATA
# =============================
df = load_budget_data()

df["Príjmy"] = df["Príjmy"].apply(clean_number)
df["Výdavky"] = df["Výdavky"].apply(clean_number)
df["Rozdiel"] = df["Rozdiel"].apply(clean_number)
df["Rok"] = df["Rok"].astype(int)

df = df.sort_values("Rok").reset_index(drop=True)

df["Efektivita"] = df["Príjmy"] / df["Výdavky"]
df["Príjmy_change_%"] = df["Príjmy"].pct_change() * 100
df["Výdavky_change_%"] = df["Výdavky"].pct_change() * 100


# =============================
# FILTERS
# =============================
min_year = int(df["Rok"].min())
max_year = int(df["Rok"].max())

if "budget_year_range" not in st.session_state:
    st.session_state["budget_year_range"] = (min_year, max_year)

if "budget_view" not in st.session_state:
    st.session_state["budget_view"] = "Oboje"


def reset_budget_filters():
    st.session_state["budget_year_range"] = (min_year, max_year)
    st.session_state["budget_view"] = "Oboje"


st.sidebar.header("Filtre rozpočtu")

selected_year_range = st.sidebar.slider(
    "Rozsah rokov",
    min_year,
    max_year,
    (min_year, max_year),
    key="budget_year_range"
)

selected_view = st.sidebar.selectbox(
    "Zobrazenie",
    ["Oboje", "Príjmy", "Výdavky"],
    key="budget_view"
)

st.sidebar.markdown("---")
st.sidebar.button("🔄 Resetovať filtre", on_click=reset_budget_filters)


# =============================
# FILTERED DATA
# =============================
df_filtered = df[
    (df["Rok"] >= selected_year_range[0]) &
    (df["Rok"] <= selected_year_range[1])
].copy()





# =============================
# TABS
# =============================
tab1, tab2, tab3 = st.tabs([
    "Prehľad",
    "Príjmy a výdavky",
    "Trendy a efektivita"
])


# =============================
# TAB 1 - PREHĽAD
# =============================
with tab1:
    st.header("Rýchly prehľad")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Počiatočný rok", int(df_filtered["Rok"].min()))

    with col2:
        st.metric("Posledný rok", int(df_filtered["Rok"].max()))

    with col3:
        st.metric("Priemerné príjmy", f"{df_filtered['Príjmy'].mean():,.2f}".replace(",", " "))

    with col4:
        st.metric("Priemerné výdavky", f"{df_filtered['Výdavky'].mean():,.2f}".replace(",", " "))

    st.subheader("Hlavný prehľad rozpočtu")

    if selected_view == "Oboje":
        fig1 = px.line(
            df_filtered,
            x="Rok",
            y=["Príjmy", "Výdavky"],
            title="Vývoj príjmov a výdavkov mesta v čase"
        )
    elif selected_view == "Príjmy":
        fig1 = px.line(
            df_filtered,
            x="Rok",
            y="Príjmy",
            title="Vývoj príjmov mesta v čase"
        )
    else:
        fig1 = px.line(
            df_filtered,
            x="Rok",
            y="Výdavky",
            title="Vývoj výdavkov mesta v čase"
        )

    st.plotly_chart(fig1, use_container_width=True, key="budget_overview_chart")

    best_income_year = df_filtered.loc[df_filtered["Príjmy"].idxmax(), "Rok"]
    best_expense_year = df_filtered.loc[df_filtered["Výdavky"].idxmax(), "Rok"]

    st.subheader("Stručné zhrnutie")
    st.write(
        f"Najvyššie príjmy boli zaznamenané v roku **{int(best_income_year)}** "
        f"a najvyššie výdavky v roku **{int(best_expense_year)}**."
    )


# =============================
# TAB 2 - PRÍJMY A VÝDAVKY
# =============================
with tab2:
    st.header("Príjmy a výdavky")

    df_melt = df_filtered.melt(
        id_vars="Rok",
        value_vars=["Príjmy", "Výdavky"],
        var_name="Typ",
        value_name="Hodnota"
    )

    st.subheader("Porovnanie príjmov a výdavkov")

    fig2 = px.bar(
        df_melt,
        x="Rok",
        y="Hodnota",
        color="Typ",
        barmode="group",
        title="Porovnanie príjmov a výdavkov"
    )
    st.plotly_chart(fig2, use_container_width=True, key="budget_compare_chart")

    st.subheader("Rozdiel medzi príjmami a výdavkami")

    fig3 = px.bar(
        df_filtered,
        x="Rok",
        y="Rozdiel",
        title="Rozdiel medzi príjmami a výdavkami"
    )
    st.plotly_chart(fig3, use_container_width=True, key="budget_difference_chart")


# =============================
# TAB 3 - TRENDY A EFEKTIVITA
# =============================
with tab3:
    st.header("Trendy a efektivita")

    st.subheader("Efektivita hospodárenia mesta")

    fig4 = px.line(
        df_filtered,
        x="Rok",
        y="Efektivita",
        title="Efektivita hospodárenia mesta"
    )
    st.plotly_chart(fig4, use_container_width=True, key="budget_efficiency_chart")

    st.subheader("Percentuálna zmena príjmov")

    fig5 = px.line(
        df_filtered[df_filtered["Rok"] != df_filtered["Rok"].min()],
        x="Rok",
        y="Príjmy_change_%",
        title="Percentuálna zmena príjmov (%)"
    )
    st.plotly_chart(fig5, use_container_width=True, key="budget_income_change_chart")

    st.subheader("Percentuálna zmena výdavkov")

    fig6 = px.line(
        df_filtered[df_filtered["Rok"] != df_filtered["Rok"].min()],
        x="Rok",
        y="Výdavky_change_%",
        title="Percentuálna zmena výdavkov (%)"
    )
    st.plotly_chart(fig6, use_container_width=True, key="budget_expense_change_chart")