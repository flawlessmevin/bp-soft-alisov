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
# =============================
# SIDEBAR
# =============================

min_year = int(df["Rok"].min())
max_year = int(df["Rok"].max())
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


debt_range_sidebar = st.sidebar.slider(
    "Rozsah aktuálneho nedoplatku (€)",
    min_value=float(df_debtors["nedoplatok"].min()),
    max_value=float(df_debtors["nedoplatok"].max()),
    value=(
        float(df_debtors["nedoplatok"].min()),
        float(df_debtors["nedoplatok"].max())
    ),
    key="debt_range_sidebar"
)

only_increased_debt_sidebar = st.sidebar.checkbox(
    "Iba dlžníci s nárastom dlhu",
    value=False,
    key="only_increased_debt_sidebar"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Dodávateľské faktúry")


order_price_range = st.sidebar.slider(
    "Cenový rozsah objednávok",
    min_value=0.0,
    max_value=float(df_orders["cena"].max()),
    value=(0.0, float(df_orders["cena"].max())),
    key="order_price_range"
)

available_years = sorted(df_orders["rok"].dropna().unique().tolist())
selected_order_year = st.sidebar.selectbox(
    "Rok objednávok",
    ["Všetky"] + [int(y) for y in available_years],
    key="selected_order_year"
)


df_filtered = df[
    (df["Rok"] >= selected_year_range[0]) &
    (df["Rok"] <= selected_year_range[1])
].copy()
df_orders_filtered = df_orders.copy()

df_orders_filtered = df_orders[
    (df_orders["cena"].between(order_price_range[0], order_price_range[1]))
].copy()

if selected_order_year != "Všetky":
    df_orders_filtered = df_orders_filtered[
        df_orders_filtered["rok"] == selected_order_year
    ]










st.sidebar.markdown("---")
st.sidebar.button("🔄 Resetovať filtre", on_click=reset_filters)


# =============================
# TABS
# =============================
tab1, tab2, tab3,  = st.tabs([
    "Príjmy a výdavky",
    "Daňoví dlžníci",
    "Dodávateľské faktúry"
])
# =============================
# TAB 1 - PRÍJMY A VÝDAVKY
# =============================
with tab1:
    st.subheader("Príjmy a výdavky")

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

    st.markdown("---")

    st.subheader("Súhrnné štatistiky príjmov a výdavok ")

    max_income_row = df_filtered.loc[df_filtered["Príjmy"].idxmax()]
    max_expense_row = df_filtered.loc[df_filtered["Výdavky"].idxmax()]
    max_surplus_row = df_filtered.loc[df_filtered["Rozdiel"].idxmax()]
    min_surplus_row = df_filtered.loc[df_filtered["Rozdiel"].idxmin()]

    total_income = df_filtered["Príjmy"].sum()
    total_expense = df_filtered["Výdavky"].sum()
    average_efficiency = df_filtered["Efektivita"].mean()

    overall_balance = total_income - total_expense

    summary_table_budget = pd.DataFrame({
        "Ukazovateľ": [
            "Rok s najvyššími príjmami",
            "Rok s najvyššími výdavkami",
            "Rok s najväčším prebytkom",
            "Rok s najväčším schodkom",
            "Celkové príjmy za sledované obdobie",
            "Celkové výdavky za sledované obdobie",
            "Priemerná efektívnosť riadenia",
            "Celkový výsledok riadenia"
        ],
        "Hodnota": [
            f"{int(max_income_row['Rok'])} ({max_income_row['Príjmy']:,.2f} €)".replace(",", " "),
            f"{int(max_expense_row['Rok'])} ({max_expense_row['Výdavky']:,.2f} €)".replace(",", " "),
            f"{int(max_surplus_row['Rok'])} ({max_surplus_row['Rozdiel']:,.2f} €)".replace(",", " "),
            f"{int(min_surplus_row['Rok'])} ({min_surplus_row['Rozdiel']:,.2f} €)".replace(",", " "),
            f"{total_income:,.2f} €".replace(",", " "),
            f"{total_expense:,.2f} €".replace(",", " "),
            f"{average_efficiency:.2f} %",
            f"{overall_balance:,.2f} €".replace(",", " ")
        ]
    })

    st.dataframe(summary_table_budget, use_container_width=True, hide_index=True)
    st.markdown("---")
    st.caption("Zdroj dát: [Mesto Nitra - OPEN DATA](https://klient.nitra.sk/default.aspx?NavigationState=1100:0:)")


# =============================
# TAB 2 -  "Daňoví dlžníci"
# =============================
with tab2:
    st.header("Daňoví dlžníci")

    df_debtors_nitra = df_debtors[
        df_debtors["mesto"].astype(str).str.strip().str.lower() == "nitra"
    ].copy()

    df_debtors_nitra["dlznik"] = df_debtors_nitra["dlznik"].fillna("").astype(str)
    df_debtors_nitra["adresa"] = df_debtors_nitra["adresa"].fillna("").astype(str)
    df_debtors_nitra["mesto"] = df_debtors_nitra["mesto"].fillna("").astype(str)
    df_debtors_nitra["mena"] = df_debtors_nitra["mena"].fillna("EUR").astype(str)

    df_debtors_nitra["nedoplatok"] = pd.to_numeric(
        df_debtors_nitra["nedoplatok"], errors="coerce"
    ).fillna(0)

    df_debtors_nitra["nedoplatok_minuly"] = pd.to_numeric(
        df_debtors_nitra["nedoplatok_minuly"], errors="coerce"
    ).fillna(0)

    df_debtors_nitra["zmena_nedoplatku"] = (
        df_debtors_nitra["nedoplatok"] - df_debtors_nitra["nedoplatok_minuly"]
    )

    df_debtors_graph = df_debtors_nitra[
        df_debtors_nitra["nedoplatok"].between(
            debt_range_sidebar[0],
            debt_range_sidebar[1]
        )
    ].copy()

    if only_increased_debt_sidebar:
        df_debtors_graph = df_debtors_graph[
            df_debtors_graph["zmena_nedoplatku"] > 0
            ]

    if df_debtors_nitra.empty:
        st.warning("V datasete sa nenašli žiadni daňoví dlžníci pre mesto Nitra.")
    else:
        total_current_debt = df_debtors_nitra["nedoplatok"].sum()
        total_previous_debt = df_debtors_nitra["nedoplatok_minuly"].sum()
        total_debtors = len(df_debtors_nitra)
        average_debt = df_debtors_nitra["nedoplatok"].mean()
        median_debt = df_debtors_nitra["nedoplatok"].median()
        increased_count = (df_debtors_nitra["zmena_nedoplatku"] > 0).sum()

        top_debtor_row = df_debtors_nitra.loc[df_debtors_nitra["nedoplatok"].idxmax()]

        top_debtors_current = (
            df_debtors_graph
            .sort_values("nedoplatok", ascending=False)
            .head(10)
            .copy()
        )

        fig_debt_1 = px.bar(
            top_debtors_current.sort_values("nedoplatok", ascending=True),
            x="nedoplatok",
            y="dlznik",
            orientation="h",
            text="nedoplatok",
            labels={
                "nedoplatok": "Suma nedoplatku (€)",
                "dlznik": "Dlžník"
            },
            title="10 najväčších daňových dlžníkov v meste Nitra"
        )

        fig_debt_1.update_traces(
            texttemplate="%{text:.2f} €",
            textposition="outside"
        )

        fig_debt_1.update_layout(
            xaxis_title="Suma nedoplatku (€)",
            yaxis_title="Dlžník",
            height=600
        )

        st.plotly_chart(
            fig_debt_1,
            use_container_width=True,
            key="debtors_nitra_top_current_chart"
        )











        bins = [0, 100, 500, 1000, 5000, 10000, float("inf")]
        labels = [
            "0 – 99 €",
            "100 – 499 €",
            "500 – 999 €",
            "1 000 – 4 999 €",
            "5 000 – 9 999 €",
            "10 000 € a viac"
        ]

        df_debtors_nitra["pasmo_nedoplatku"] = pd.cut(
            df_debtors_nitra["nedoplatok"],
            bins=bins,
            labels=labels,
            right=False,
            include_lowest=True
        )

        debt_distribution = (
            df_debtors_nitra.groupby("pasmo_nedoplatku", as_index=False)
            .size()
            .rename(columns={"size": "pocet_dlznikov"})
        )

        fig_debt_3 = px.bar(
            debt_distribution,
            x="pasmo_nedoplatku",
            y="pocet_dlznikov",
            text="pocet_dlznikov",
            labels={
                "pasmo_nedoplatku": "Pásmo nedoplatku",
                "pocet_dlznikov": "Počet dlžníkov"
            },
            title="Rozdelenie daňových dlžníkov podľa výšky nedoplatku"
        )

        fig_debt_3.update_traces(textposition="outside")

        fig_debt_3.update_layout(
            xaxis_title="Pásmo nedoplatku",
            yaxis_title="Počet dlžníkov"
        )

        st.plotly_chart(
            fig_debt_3,
            use_container_width=True,
            key="debtors_nitra_distribution_chart"
        )
        st.markdown("---")
        st.subheader("Detail dlžníka")
        with st.expander("Vyber dlžníka", expanded=False):
            debtor_search = st.text_input(
                "Vyhľadávanie podľa mena alebo adresy",
                placeholder="Zadajte meno dlžníka alebo časť adresy",
                key="debtor_search_input"
            )

            min_debt = float(df_debtors_nitra["nedoplatok"].min())
            max_debt = float(df_debtors_nitra["nedoplatok"].max())

            debtor_range = st.slider(
                "Rozsah aktuálneho nedoplatku (€)",
                min_value=min_debt,
                max_value=max_debt,
                value=(min_debt, max_debt),
                key="debtor_range_slider"
            )

            df_debtor_detail = df_debtors_nitra[
                df_debtors_nitra["nedoplatok"].between(debtor_range[0], debtor_range[1])
            ].copy()

            if debtor_search:
                debtor_search_lower = debtor_search.lower()
                df_debtor_detail = df_debtor_detail[
                    df_debtor_detail["dlznik"].str.lower().str.contains(debtor_search_lower, na=False)
                    | df_debtor_detail["adresa"].str.lower().str.contains(debtor_search_lower, na=False)
                    ]

            df_debtor_detail = df_debtor_detail.sort_values("nedoplatok", ascending=False).copy()

            st.caption(f"Nájdených dlžníkov: {len(df_debtor_detail)}")

            if not df_debtor_detail.empty:
                selected_debtor_idx = st.selectbox(
                    "Vyber dlžníka",
                    df_debtor_detail.index.tolist(),
                    format_func=lambda idx: (
                        f"{df_debtor_detail.loc[idx, 'dlznik']} | "
                        f"{df_debtor_detail.loc[idx, 'adresa']} | "
                        f"{df_debtor_detail.loc[idx, 'nedoplatok']:,.2f} €"
                    ).replace(",", " "),
                    key="selected_debtor_detail"
                )

                selected_debtor = df_debtor_detail.loc[selected_debtor_idx]

                st.markdown(f"### {selected_debtor['dlznik']}")

                col5, col6, col7 = st.columns(3)

                with col5:
                    st.metric(
                        "Aktuálny nedoplatok",
                        f"{selected_debtor['nedoplatok']:,.2f} €".replace(",", " ")
                    )

                with col6:
                    st.metric(
                        "Minulý nedoplatok",
                        f"{selected_debtor['nedoplatok_minuly']:,.2f} €".replace(",", " ")
                    )

                with col7:
                    st.metric(
                        "Zmena",
                        f"{selected_debtor['zmena_nedoplatku']:,.2f} €".replace(",", " ")
                    )

                debtor_detail_table = pd.DataFrame({
                    "Pole": [
                        "Dlžník",
                        "Adresa",
                        "Mesto",
                        "Aktuálny nedoplatok",
                        "Minulý nedoplatok",
                        "Zmena nedoplatku",
                        "Mena"
                    ],
                    "Hodnota": [
                        selected_debtor["dlznik"] if selected_debtor["dlznik"] else "-",
                        selected_debtor["adresa"] if selected_debtor["adresa"] else "-",
                        selected_debtor["mesto"] if selected_debtor["mesto"] else "-",
                        f"{selected_debtor['nedoplatok']:,.2f} €".replace(",", " "),
                        f"{selected_debtor['nedoplatok_minuly']:,.2f} €".replace(",", " "),
                        f"{selected_debtor['zmena_nedoplatku']:,.2f} €".replace(",", " "),
                        selected_debtor["mena"] if selected_debtor["mena"] else "-"
                    ]
                })

                st.dataframe(
                    debtor_detail_table,
                    use_container_width=True,
                    hide_index=True
                )

                debtor_compare_df = pd.DataFrame({
                    "Obdobie": ["Minulý nedoplatok", "Aktuálny nedoplatok"],
                    "Suma": [
                        selected_debtor["nedoplatok_minuly"],
                        selected_debtor["nedoplatok"]
                    ]
                })

                fig_debt_4 = px.bar(
                    debtor_compare_df,
                    x="Obdobie",
                    y="Suma",
                    text="Suma",
                    labels={"Obdobie": "Obdobie", "Suma": "Suma (€)"},
                    title=f"Porovnanie nedoplatku dlžníka: {selected_debtor['dlznik']}"
                )

                fig_debt_4.update_traces(
                    texttemplate="%{text:.2f} €",
                    textposition="outside"
                )

                st.plotly_chart(
                    fig_debt_4,
                    use_container_width=True,
                    key="selected_debtor_compare_chart"
                )

            else:
                st.info("Pre zadané filtre sa nenašiel žiadny dlžník.")

        st.markdown("---")

        st.subheader("Súhrnné štatistiky dlžníkov")

        max_debtor_row = df_debtors_nitra.loc[df_debtors_nitra["nedoplatok"].idxmax()]
        max_increase_row = df_debtors_nitra.loc[df_debtors_nitra["zmena_nedoplatku"].idxmax()]
        max_decrease_row = df_debtors_nitra.loc[df_debtors_nitra["zmena_nedoplatku"].idxmin()]

        summary_table_debtors = pd.DataFrame({
            "Ukazovateľ": [
                "Počet daňových dlžníkov v meste Nitra",
                "Celkový aktuálny nedoplatok",
                "Celkový minulý nedoplatok",
                "Priemerný nedoplatok",
                "Najväčší dlžník podľa aktuálnej sumy",
                "Najväčší nárast nedoplatku",
                "Najväčší pokles nedoplatku"
            ],
            "Hodnota": [
                f"{total_debtors}",
                f"{total_current_debt:,.2f} €".replace(",", " "),
                f"{total_previous_debt:,.2f} €".replace(",", " "),
                f"{average_debt:,.2f} €".replace(",", " "),
                f"{max_debtor_row['dlznik']} ({max_debtor_row['nedoplatok']:,.2f} €)".replace(",", " "),
                f"{max_increase_row['dlznik']} ({max_increase_row['zmena_nedoplatku']:,.2f} €)".replace(",", " "),
                f"{max_decrease_row['dlznik']} ({max_decrease_row['zmena_nedoplatku']:,.2f} €)".replace(",", " ")
            ]
        })

        st.dataframe(
            summary_table_debtors,
            use_container_width=True,
            hide_index=True
        )
        st.markdown("---")
        st.caption("Zdroj dát: [Mesto Nitra - OPEN DATA](https://klient.nitra.sk/default.aspx?NavigationState=1100:0:)")
with tab3:
    st.header("Dodávateľské faktúry")



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
    st.markdown("---")
    st.subheader("Najväčšie objednávky")

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

    st.markdown("---")
    st.subheader("Detail dodávateľa")
    with st.expander("Vyber dodávateľa", expanded=False):
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

    st.markdown("---")
    st.subheader("Detail objednávky")
    with st.expander("Vyber objednávky"):
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
            filtered_order_detail["datum_text"] = filtered_order_detail["datum_vystavenia"].dt.strftime(
                "%d.%m.%Y").fillna(
                "")

            filtered_order_detail["select_label"] = (
                    filtered_order_detail["cislo_faktury"].replace("", "Bez čísla")
                    + " | "
                    + filtered_order_detail["dodavatel"].replace("", "Neznámy dodávateľ").str[:35]
                    + " | "
                    + filtered_order_detail["predmet"].replace("", "Bez predmetu").str[:45]
                    + " | "
                    + filtered_order_detail["datum_text"]
                    + " | "
                    + filtered_order_detail["cena"].map(lambda x: f"{x:,.2f} €".replace(",", " "))
            )

            selected_order_idx = st.selectbox(
                "Vyber objednávku",
                filtered_order_detail.index.tolist(),
                format_func=lambda idx: filtered_order_detail.loc[idx, "select_label"],
                key="selected_order_detail_record"
            )

            selected_order = filtered_order_detail.loc[selected_order_idx]

            st.markdown("### Vybraná objednávka")

            col1, col2, col3 = st.columns(3)

            order_date = selected_order["datum_vystavenia"]
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
            st.warning("Pre zadané filtre sa nenašla žiadna objednávka.")

    st.markdown("---")
    st.subheader("Súhrnné štatistiky objednávok")

    top_supplier_sum_row = top_suppliers.iloc[0]
    top_supplier_count_row = top_suppliers_count.iloc[0]
    top_order_day_row = orders_by_date.loc[orders_by_date["cena"].idxmax()]

    total_orders = len(df_orders_filtered)
    total_orders_sum = df_orders_filtered["cena"].sum()
    average_order_value = df_orders_filtered["cena"].mean()

    summary_table_orders = pd.DataFrame({
        "Ukazovateľ": [
            "Celkový počet objednávok",
            "Celkový objem objednávok",
            "Priemerná hodnota objednávky",
            "Dodávateľ s najvyšším objemom objednávok",
            "Dodávateľ s najvyšším počtom objednávok",
            "Deň s najvyšším objemom objednávok"
        ],
        "Hodnota": [
            f"{total_orders}",
            f"{total_orders_sum:,.2f} €".replace(",", " "),
            f"{average_order_value:,.2f} €".replace(",", " "),
            f"{top_supplier_sum_row['dodavatel']} ({top_supplier_sum_row['cena']:,.2f} €)".replace(",", " "),
            f"{top_supplier_count_row['dodavatel']} ({int(top_supplier_count_row['pocet_objednavok'])})",
            f"{pd.to_datetime(top_order_day_row['datum_vystavenia']).strftime('%d.%m.%Y')} ({top_order_day_row['cena']:,.2f} €)".replace(
                ",", " ")
        ]
    })

    st.dataframe(summary_table_orders, use_container_width=True, hide_index=True)
    st.markdown("---")
    st.caption("Zdroj dát: [Mesto Nitra - OPEN DATA](https://klient.nitra.sk/default.aspx?NavigationState=1100:0:)")