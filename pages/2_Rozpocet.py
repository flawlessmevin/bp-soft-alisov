import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_budget_data, load_orders_data, load_debtors_data

st.title("Rozpočet mesta Nitra")

st.write("""
Táto sekcia zobrazuje analýzu rozpočtových údajov mesta Nitra.
""")



# =============================
# LOAD DATA
# =============================
df = load_budget_data()
df_debtors = load_debtors_data()
df_orders = load_orders_data()



min_year = int(df["Rok"].min())
max_year = int(df["Rok"].max())

# =============================
# SIDEBAR
# =============================
def reset_filters():
    st.session_state["budget_year_range"] = (min_year, max_year)
    st.session_state["budget_view"] = "Oboje"
st.sidebar.subheader("Príjmy a výdavky")
selected_year_range = st.sidebar.slider(
    "Rozsah rokov",
    min_year,
    max_year,
    (min_year, max_year),
    key="budget_year_range"
)
st.sidebar.markdown("---")
st.sidebar.subheader("Daňoví dlžníci")

st.sidebar.markdown("---")
st.sidebar.subheader("Objednávky")

min_order_price = st.sidebar.slider(
    "Minimálna cena objednávky",
    0.0,
    float(df_orders["cena"].max()),
    0.0,
    key="min_order_price"
)

available_years = sorted(df_orders["rok"].dropna().unique().tolist())
selected_order_year = st.sidebar.selectbox(
    "Rok objednávok",
    ["Všetky"] + [int(y) for y in available_years],
    key="selected_order_year"
)

order_sort_by = st.sidebar.selectbox(
    "Triediť objednávky podľa",
    ["Dátum vystavenia", "Cena - vzostupne", "Cena - zostupne"],
    key="order_sort_by"
)










st.sidebar.markdown("---")
st.sidebar.button("🔄 Resetovať filtre", on_click=reset_filters)

# =============================
# FILTERS
# =============================















# =============================
# FILTERED DATA
# =============================
df_filtered = df[
    (df["Rok"] >= selected_year_range[0]) &
    (df["Rok"] <= selected_year_range[1])
].copy()
df_orders_filtered = df_orders.copy()

df_orders_filtered = df_orders_filtered[
    df_orders_filtered["cena"] >= min_order_price
]

if selected_order_year != "Všetky":
    df_orders_filtered = df_orders_filtered[
        df_orders_filtered["rok"] == selected_order_year
    ]

if order_sort_by == "Dátum vystavenia":
    df_orders_filtered = df_orders_filtered.sort_values("datum_vystavenia")
elif order_sort_by == "Cena - vzostupne":
    df_orders_filtered = df_orders_filtered.sort_values("cena", ascending=True)
elif order_sort_by == "Cena - zostupne":
    df_orders_filtered = df_orders_filtered.sort_values("cena", ascending=False)




# =============================
# TABS
# =============================
tab1, tab2, tab3,  = st.tabs([
    "Príjmy a výdavky",
    "Daňoví dlžníci",
    "Objednávky"
])

# =============================
# TAB 1 - PRÍJMY A VÝDAVKY
# =============================
with tab1:
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

    fig4 = px.line(
        df_filtered,
        x="Rok",
        y="Efektivita",
        title="Efektivita hospodárenia mesta"
    )
    st.plotly_chart(fig4, use_container_width=True, key="budget_efficiency_chart")

    fig5 = px.line(
        df_filtered[df_filtered["Rok"] != df_filtered["Rok"].min()],
        x="Rok",
        y="Príjmy_change_%",
        title="Percentuálna zmena príjmov (%)"
    )
    st.plotly_chart(fig5, use_container_width=True, key="budget_income_change_chart")

    fig6 = px.line(
        df_filtered[df_filtered["Rok"] != df_filtered["Rok"].min()],
        x="Rok",
        y="Výdavky_change_%",
        title="Percentuálna zmena výdavkov (%)"
    )
    st.plotly_chart(fig6, use_container_width=True, key="budget_expense_change_chart")



# =============================
# TAB 2 -  "Daňoví dlžníci"
# =============================
with tab2:
    st.header("Daňoví dlžníci")

    with st.expander("Filtre daňových dlžníkov", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            debtor_search = st.text_input("Vyhľadať dlžníka", "", key="debtor_search")

        with col2:
            debtor_city = st.selectbox(
                "Mesto",
                ["Všetky"] + sorted(df_debtors["mesto"].dropna().unique().tolist()),
                key="debtor_city"
            )

        with col3:
            min_debt = st.slider(
                "Minimálna suma nedoplatku",
                0.0,
                float(df_debtors["nedoplatok"].max()),
                0.0,
                key="min_debt"
            )

    df_debtors_filtered = df_debtors.copy()

    if debtor_search:
        df_debtors_filtered = df_debtors_filtered[
            df_debtors_filtered["dlznik"].str.contains(debtor_search, case=False, na=False)
        ]

    if debtor_city != "Všetky":
        df_debtors_filtered = df_debtors_filtered[
            df_debtors_filtered["mesto"] == debtor_city
            ]

    df_debtors_filtered = df_debtors_filtered[
        df_debtors_filtered["nedoplatok"] >= min_debt
        ]

    top_debtors = df_debtors_filtered.sort_values("nedoplatok", ascending=False).head(10)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Počet dlžníkov", len(df_debtors_filtered))

    with col2:
        st.metric("Súčet nedoplatkov", f"{df_debtors_filtered['nedoplatok'].sum():,.2f}".replace(",", " "))

    with col3:
        st.metric("Najvyšší nedoplatok", f"{df_debtors_filtered['nedoplatok'].max():,.2f}".replace(",", " "))

    st.subheader("Top 10 daňových dlžníkov")

    fig_debt_1 = px.bar(
        top_debtors.sort_values("nedoplatok", ascending=True),
        x="nedoplatok",
        y="dlznik",
        orientation="h",
        labels={"nedoplatok": "Suma nedoplatku", "dlznik": "Dlžník"},
        title="Top 10 daňových dlžníkov podľa aktuálnej sumy"
    )
    st.plotly_chart(fig_debt_1, use_container_width=True, key="debtors_top_chart")

    st.subheader("Porovnanie minulého a aktuálneho nedoplatku")

    debt_compare = top_debtors.melt(
        id_vars="dlznik",
        value_vars=["nedoplatok_minuly", "nedoplatok"],
        var_name="obdobie",
        value_name="suma"
    )

    debt_compare["obdobie"] = debt_compare["obdobie"].replace({
        "nedoplatok_minuly": "Predchádzajúci rok",
        "nedoplatok": "Aktuálny stav"
    })

    fig_debt_2 = px.bar(
        debt_compare,
        x="dlznik",
        y="suma",
        color="obdobie",
        barmode="group",
        labels={"dlznik": "Dlžník", "suma": "Suma", "obdobie": "Obdobie"},
        title="Porovnanie nedoplatkov"
    )
    st.plotly_chart(fig_debt_2, use_container_width=True, key="debtors_compare_chart")

    st.subheader("Súčet nedoplatkov podľa mesta")

    debt_by_city = (
        df_debtors_filtered.groupby("mesto", as_index=False)["nedoplatok"]
        .sum()
        .sort_values("nedoplatok", ascending=False)
        .head(10)
    )

    fig_debt_3 = px.bar(
        debt_by_city,
        x="mesto",
        y="nedoplatok",
        labels={"mesto": "Mesto", "nedoplatok": "Suma nedoplatku"},
        title="Top mestá podľa sumy daňových nedoplatkov"
    )
    st.plotly_chart(fig_debt_3, use_container_width=True, key="debtors_city_chart")


with tab3:
    st.header("Objednávky")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Počet objednávok", len(df_orders_filtered))

    with col2:
        st.metric(
            "Celková suma",
            f"{df_orders_filtered['cena'].sum():,.2f}".replace(",", " ")
        )

    with col3:
        st.metric(
            "Najväčšia objednávka",
            f"{df_orders_filtered['cena'].max():,.2f}".replace(",", " ")
        )

    # =============================
    # 1. Vývoj objemu objednávok v čase
    # =============================
    st.subheader("Vývoj objemu objednávok v čase")

    orders_by_date = (
        df_orders_filtered.groupby("datum_vystavenia", as_index=False)["cena"]
        .sum()
        .sort_values("datum_vystavenia")
    )

    fig_orders_1 = px.line(
        orders_by_date,
        x="datum_vystavenia",
        y="cena",
        labels={"datum_vystavenia": "Dátum", "cena": "Suma"},
        title="Vývoj objemu objednávok v čase"
    )
    st.plotly_chart(fig_orders_1, use_container_width=True, key="orders_time_chart")

    # =============================
    # 2. Top dodávatelia
    # =============================
    st.subheader("Top dodávatelia podľa celkovej sumy")

    top_suppliers = (
        df_orders_filtered.groupby("dodavatel", as_index=False)["cena"]
        .sum()
        .sort_values("cena", ascending=False)
        .head(10)
    )

    fig_orders_2 = px.bar(
        top_suppliers.sort_values("cena", ascending=True),
        x="cena",
        y="dodavatel",
        orientation="h",
        labels={"dodavatel": "Dodávateľ", "cena": "Celková suma"},
        title="Top dodávatelia podľa objemu objednávok"
    )
    st.plotly_chart(fig_orders_2, use_container_width=True, key="orders_supplier_chart")

    # =============================
    # 3. Najväčšie jednotlivé objednávky
    # =============================
    st.subheader("Najväčšie jednotlivé objednávky")

    top_orders = df_orders_filtered.sort_values("cena", ascending=False).head(10)

    fig_orders_3 = px.bar(
        top_orders,
        x="dodavatel",
        y="cena",
        hover_data=["predmet", "datum_vystavenia"],
        labels={"dodavatel": "Dodávateľ", "cena": "Cena"},
        title="Najväčšie jednotlivé objednávky"
    )
    st.plotly_chart(fig_orders_3, use_container_width=True, key="orders_top_chart")





    st.subheader("Detail objednávky / dodávateľa")
    supplier_options = sorted(df_orders["dodavatel"].dropna().unique().tolist())
    supplier_options_with_empty = ["-- Vyber dodávateľa --"] + supplier_options

    selected_supplier_detail = st.selectbox(
        "Vyber dodávateľa",
        supplier_options_with_empty,
        key="selected_supplier_detail"
    )

    if selected_supplier_detail != "-- Vyber dodávateľa --":
        df_supplier_detail = df_orders[
            df_orders["dodavatel"] == selected_supplier_detail
            ].copy()

        st.markdown(f"### Dodávateľ: {selected_supplier_detail}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Počet objednávok", len(df_supplier_detail))

        with col2:
            st.metric(
                "Celková suma",
                f"{df_supplier_detail['cena'].sum():,.2f}".replace(",", " ")
            )

        with col3:
            st.metric(
                "Najväčšia objednávka",
                f"{df_supplier_detail['cena'].max():,.2f}".replace(",", " ")
            )

        st.subheader("Objednávky vybraného dodávateľa")

        st.dataframe(
            df_supplier_detail[
                ["cislo_faktury", "predmet", "cena", "datum_vystavenia", "ico"]
            ].sort_values("cena", ascending=False),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Vývoj objednávok dodávateľa v čase")

        supplier_by_date = (
            df_supplier_detail.groupby("datum_vystavenia", as_index=False)["cena"]
            .sum()
            .sort_values("datum_vystavenia")
        )

        fig_supplier_detail_1 = px.line(
            supplier_by_date,
            x="datum_vystavenia",
            y="cena",
            labels={"datum_vystavenia": "Dátum", "cena": "Suma"},
            title=f"Vývoj objednávok dodávateľa {selected_supplier_detail}"
        )
        st.plotly_chart(fig_supplier_detail_1, use_container_width=True, key="supplier_detail_time")

        st.subheader("Najväčšie objednávky dodávateľa")

        top_supplier_orders = df_supplier_detail.sort_values("cena", ascending=False).head(10)

        fig_supplier_detail_2 = px.bar(
            top_supplier_orders,
            x="datum_vystavenia",
            y="cena",
            hover_data=["predmet"],
            labels={"datum_vystavenia": "Dátum", "cena": "Cena"},
            title=f"Najväčšie objednávky dodávateľa {selected_supplier_detail}"
        )
        st.plotly_chart(fig_supplier_detail_2, use_container_width=True, key="supplier_detail_top")

    else:
        st.info("Vyberte dodávateľa, aby sa zobrazili podrobné informácie.")

