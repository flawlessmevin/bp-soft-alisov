import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_budget_data, load_orders_data, load_debtors_data

st.title("Rozpočet mesta Nitra")





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


    df_melt = df_filtered.melt(
        id_vars="Rok",
        value_vars=["Príjmy", "Výdavky"],
        var_name="Typ",
        value_name="Hodnota"
    )



    fig2 = px.bar(
        df_melt,
        x="Rok",
        y="Hodnota",
        color="Typ",
        barmode="group",
        title="Porovnanie príjmov a výdavkov"
    )
    st.plotly_chart(fig2, use_container_width=True, key="budget_compare_chart")



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

    df_debtors_filtered = df_debtors.copy()

    top_debtors = df_debtors_filtered.sort_values("nedoplatok", ascending=False).head(10)

    fig_debt_1 = px.bar(
        top_debtors.sort_values("nedoplatok", ascending=True),
        x="nedoplatok",
        y="dlznik",
        orientation="h",
        labels={"nedoplatok": "Suma nedoplatku", "dlznik": "Dlžník"},
        title="Top 10 daňových dlžníkov podľa aktuálnej sumy"
    )
    st.plotly_chart(fig_debt_1, use_container_width=True, key="debtors_top_chart")







    top_debtors = (
        df_debtors_filtered[
            df_debtors_filtered["mesto"].astype(str).str.strip().str.lower() == "nitra"
            ]
        .sort_values("nedoplatok", ascending=False)
        .head(10)
        .copy()
    )

    fig_debt_3 = px.bar(
        top_debtors.sort_values("nedoplatok", ascending=True),
        x="nedoplatok",
        y="dlznik",
        orientation="h",
        text="nedoplatok",
        labels={
            "dlznik": "Dlžník",
            "nedoplatok": "Suma nedoplatku (€)"
        },
        title="Top dlžníci podľa výšky nedoplatku v meste Nitra"
    )

    fig_debt_3.update_traces(
        texttemplate="%{text:.2f} €",
        textposition="outside"
    )

    fig_debt_3.update_layout(
        xaxis_title="Suma nedoplatku (€)",
        yaxis_title="Dlžník",
        height=600
    )

    st.plotly_chart(fig_debt_3, use_container_width=True, key="debtors_nitra_top_chart")


with tab3:
    st.header("Objednávky")



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
        text="cena",
        labels={"dodavatel": "Dodávateľ", "cena": "Celková suma"},
        title="Top dodávatelia podľa objemu objednávok"
    )

    fig_orders_2.update_traces(
        texttemplate="%{text:.2f} €",
        textposition="outside"
    )

    st.plotly_chart(fig_orders_2, use_container_width=True, key="orders_supplier_chart")



    top_suppliers_count = (
        df_orders_filtered.groupby("dodavatel", as_index=False)
        .size()
        .rename(columns={"size": "pocet_objednavok"})
        .sort_values("pocet_objednavok", ascending=False)
        .head(10)
    )

    fig_orders_3 = px.bar(
        top_suppliers_count.sort_values("pocet_objednavok", ascending=True),
        x="pocet_objednavok",
        y="dodavatel",
        orientation="h",
        text="pocet_objednavok",
        labels={
            "dodavatel": "Dodávateľ",
            "pocet_objednavok": "Počet objednávok"
        },
        title="Top dodávatelia podľa počtu objednávok"
    )
    fig_orders_3.update_traces(textposition="outside")

    st.plotly_chart(fig_orders_3, use_container_width=True, key="orders_supplier_count_chart")




    top_orders = (
        df_orders_filtered
        .sort_values("cena", ascending=False)
        .head(10)
        .copy()
    )

    top_orders_table = top_orders[[
        "cena",
        "predmet",
        "dodavatel",
        "datum_vystavenia"

    ]].rename(columns={
        "datum_vystavenia": "Dátum vystavenia",
        "dodavatel": "Dodávateľ",
        "predmet": "Predmet",
        "cena": "Cena (€)"
    })

    st.dataframe(
        top_orders_table,
        use_container_width=True,
        hide_index=True
    )





    st.subheader("Detail dodávateľa")
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



        st.dataframe(
            df_supplier_detail[
                ["cislo_faktury", "predmet", "cena", "datum_vystavenia", "ico"]
            ].sort_values("cena", ascending=False),
            use_container_width=True,
            hide_index=True
        )



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

    st.subheader("Detail objednávky")

    df_order_detail = df_orders_filtered.copy()

    df_order_detail["datum_vystavenia"] = pd.to_datetime(
        df_order_detail["datum_vystavenia"],
        errors="coerce"
    )

    df_order_detail["dodavatel"] = df_order_detail["dodavatel"].fillna("").astype(str)
    df_order_detail["predmet"] = df_order_detail["predmet"].fillna("").astype(str)
    df_order_detail["cislo_faktury"] = df_order_detail["cislo_faktury"].fillna("").astype(str)
    df_order_detail["ico"] = df_order_detail["ico"].fillna("").astype(str)

    valid_dates = df_order_detail["datum_vystavenia"].dropna()
    min_price = float(df_order_detail["cena"].min())
    max_price = float(df_order_detail["cena"].max())

    col1, col2 = st.columns(2)

    with col1:
        supplier_filter_order = st.selectbox(
            "Dodávateľ",
            ["Všetci dodávatelia"] + sorted(
                df_order_detail["dodavatel"].replace("", pd.NA).dropna().unique().tolist()
            ),
            key="supplier_filter_order"
        )

        search_invoice = st.text_input(
            "Číslo faktúry alebo IČO",
            key="search_invoice_order",
            placeholder="Napr. 2024-001 alebo 12345678"
        )

    with col2:
        search_subject = st.text_input(
            "Predmet objednávky",
            key="search_subject_order",
            placeholder="Zadajte časť názvu predmetu"
        )

        if not valid_dates.empty:
            date_range_order = st.date_input(
                "Rozsah dátumu vystavenia",
                value=(valid_dates.min().date(), valid_dates.max().date()),
                key="date_range_order"
            )
        else:
            date_range_order = ()

    search_all_order = st.text_input(
        "Rýchle fulltextové vyhľadávanie",
        key="search_all_order",
        placeholder="Dodávateľ, predmet, číslo faktúry, IČO, dátum..."
    )

    price_range_order = st.slider(
        "Rozsah ceny (€)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        key="price_range_order"
    )

    filtered_order_detail = df_order_detail.copy()

    if supplier_filter_order != "Všetci dodávatelia":
        filtered_order_detail = filtered_order_detail[
            filtered_order_detail["dodavatel"] == supplier_filter_order
            ]

    if search_invoice:
        search_invoice_lower = search_invoice.lower()
        filtered_order_detail = filtered_order_detail[
            filtered_order_detail["cislo_faktury"].str.lower().str.contains(search_invoice_lower, na=False)
            | filtered_order_detail["ico"].str.lower().str.contains(search_invoice_lower, na=False)
            ]

    if search_subject:
        search_subject_lower = search_subject.lower()
        filtered_order_detail = filtered_order_detail[
            filtered_order_detail["predmet"].str.lower().str.contains(search_subject_lower, na=False)
        ]

    if len(date_range_order) == 2:
        start_date, end_date = date_range_order
        filtered_order_detail = filtered_order_detail[
            filtered_order_detail["datum_vystavenia"].dt.date.between(start_date, end_date)
        ]

    filtered_order_detail = filtered_order_detail[
        filtered_order_detail["cena"].between(price_range_order[0], price_range_order[1])
    ]

    if search_all_order:
        search_all_lower = search_all_order.lower()
        datum_text = filtered_order_detail["datum_vystavenia"].dt.strftime("%d.%m.%Y").fillna("")

        filtered_order_detail = filtered_order_detail[
            filtered_order_detail["dodavatel"].str.lower().str.contains(search_all_lower, na=False)
            | filtered_order_detail["predmet"].str.lower().str.contains(search_all_lower, na=False)
            | filtered_order_detail["cislo_faktury"].str.lower().str.contains(search_all_lower, na=False)
            | filtered_order_detail["ico"].str.lower().str.contains(search_all_lower, na=False)
            | datum_text.str.lower().str.contains(search_all_lower, na=False)
            ]

    filtered_order_detail = filtered_order_detail.sort_values(
        ["datum_vystavenia", "cena"],
        ascending=[False, False]
    ).copy()

    st.caption(f"Nájdených objednávok: {len(filtered_order_detail)}")

    if not filtered_order_detail.empty:
        table_df = filtered_order_detail[[
            "cislo_faktury",
            "dodavatel",
            "predmet",
            "cena",
            "datum_vystavenia",
            "ico"
        ]].copy()

        table_df = table_df.rename(columns={
            "cislo_faktury": "Číslo faktúry",
            "dodavatel": "Dodávateľ",
            "predmet": "Predmet",
            "cena": "Cena (€)",
            "datum_vystavenia": "Dátum vystavenia",
            "ico": "IČO"
        })

        table_df["Dátum vystavenia"] = pd.to_datetime(
            table_df["Dátum vystavenia"],
            errors="coerce"
        ).dt.strftime("%d.%m.%Y")

        event = st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="orders_detail_table"
        )

        selected_rows = event.selection["rows"]

        if selected_rows:
            selected_row_position = selected_rows[0]
            selected_order = filtered_order_detail.iloc[selected_row_position]

            st.markdown("### Vybraná objednávka")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Cena objednávky", f"{selected_order['cena']:,.2f} €".replace(",", " "))

            with col2:
                order_date = selected_order["datum_vystavenia"]
                st.metric(
                    "Dátum vystavenia",
                    order_date.strftime("%d.%m.%Y") if pd.notna(order_date) else "-"
                )

            with col3:
                st.metric("Dodávateľ", selected_order["dodavatel"] if selected_order["dodavatel"] else "-")

            detail_table = pd.DataFrame({
                "Pole": [
                    "Číslo faktúry",
                    "Dodávateľ",
                    "Predmet",
                    "Cena (€)",
                    "Dátum vystavenia",
                    "IČO"
                ],
                "Hodnota": [
                    selected_order["cislo_faktury"] if selected_order["cislo_faktury"] else "-",
                    selected_order["dodavatel"] if selected_order["dodavatel"] else "-",
                    selected_order["predmet"] if selected_order["predmet"] else "-",
                    f"{selected_order['cena']:,.2f}".replace(",", " "),
                    order_date.strftime("%d.%m.%Y") if pd.notna(order_date) else "-",
                    selected_order["ico"] if selected_order["ico"] else "-"
                ]
            })

            st.dataframe(detail_table, use_container_width=True, hide_index=True)
        else:
            st.info("Kliknite na riadok v tabuľke, aby sa zobrazili podrobnosti objednávky.")

    else:
        st.warning("Pre zadané filtre sa nenašla žiadna objednávka.")