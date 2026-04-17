import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_age_data, load_street_data, load_population_data
st.title("Demografia mesta Nitra")

# =============================
# LOAD DATA
# =============================
df_age = load_age_data()
df_pop = load_population_data()
df_street = load_street_data()
# =============================
# SIDEBAR
# =============================
def reset_filters():
    st.session_state["age_range"] = (min_age, max_age)
    st.session_state["gender_view"] = "Spolu"
    st.session_state["year_range"] = (min_year, max_year)

    # FOR TAB 3
    st.session_state["street_metric"] = "Spolu"
    st.session_state["top_n_streets"] = 10
    st.session_state["street_search"] = ""



st.sidebar.header("Filtre stránky")


st.sidebar.subheader("Veková štruktúra")

min_age = int(df_age["vek"].min())
max_age = int(df_age["vek"].max())
min_year = int(df_pop["Rok"].min())
max_year = int(df_pop["Rok"].max())


if "age_range" not in st.session_state:
    st.session_state["age_range"] = (min_age, max_age)

if "gender_view" not in st.session_state:
    st.session_state["gender_view"] = "Všetci"

if "year_range" not in st.session_state:
    st.session_state["year_range"] = (min_year, max_year)

if "street_metric" not in st.session_state:
    st.session_state["street_metric"] = "Všetci"

if "top_n_streets" not in st.session_state:
    st.session_state["top_n_streets"] = 10

if "selected_street" not in st.session_state:
    st.session_state["selected_street"] = ""
selected_age_range = st.sidebar.slider(
    "Vekový rozsah",
    min_age,
    max_age,
    (min_age, max_age),
    key="age_range"
)

selected_gender_view = st.sidebar.selectbox(
    "Pohlavie obyvateľa",
    ["Všetci", "Muži", "Ženy"],
    key= "gender_view"
)
st.sidebar.markdown("---")

st.sidebar.subheader("Vývoj populácie")



selected_year_range = st.sidebar.slider(
    "Rozsah rokov",
    min_year,
    max_year,
    (min_year, max_year),
    key= "year_range"
)
st.sidebar.markdown("---")

st.sidebar.subheader("Ulice mesta")

street_metric = st.sidebar.selectbox(
    "Typ ubytovania",
    ["Všetci", "Na trvalom pobyte", "Na prechodnom pobyte"],
    key="street_metric"
)

top_n_streets = st.sidebar.slider(
    "Počet ulíc v grafe",
    5,
    20,
    10,
    key="top_n_streets"
)


st.sidebar.markdown("---")
st.sidebar.button("🔄 Resetovať filtre", on_click=reset_filters)
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
    "Veková štruktúra",
    "Vývoj populácie",
    "Štatistika ulíc"
])
# =============================
# TAB 1 - VEKOVÁ ŠTRUKTÚRA
# =============================
with tab1:
    st.header("Veková štruktúra")
    df_filtered = df_age[
        (df_age["vek"] >= selected_age_range[0]) &
        (df_age["vek"] <= selected_age_range[1])
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




    fig1 = px.bar(
        df_filtered,
        x="vek",
        y=y_column,
        labels={"vek": "Vek", y_column: y_label},
        title = f"{y_label} podľa veku"
    )

    st.plotly_chart(fig1, use_container_width=True)



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
        title = "Porovnanie mužov a žien podľa veku"
    )
    st.plotly_chart(fig2, use_container_width=True, key="gender_chart")



    fig3 = px.bar(
        df_grouped_filtered,
        x="vekova_skupina",
        y="pocet_spolu",
        labels={"vekova_skupina": "Veková skupina", "pocet_spolu": "Počet obyvateľov"},
        title = "Rozdelenie obyvateľov podľa vekových skupín"
    )
    st.plotly_chart(fig3, use_container_width=True, key="group_chart")



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
        title = "Porovnanie mužov a žien podľa vekových skupín"
    )
    st.plotly_chart(fig4, use_container_width=True, key="group_gender_chart")

    st.markdown("---")
    st.subheader("Súhrnné štatistiky vekovej štruktúry")

    max_age_row = df_filtered.loc[df_filtered["pocet_spolu"].idxmax() ]
    oldest_row = df_filtered.loc[df_filtered["vek"].idxmax()]

    average_age = (
            (df_filtered["vek"] * df_filtered["pocet_spolu"]).sum()
            / df_filtered["pocet_spolu"].sum()
    )

    total_men = df_filtered["muzi"].sum()
    total_women = df_filtered["zeny"].sum()
    total_population = df_filtered["pocet_spolu"].sum()

    men_share = (total_men / total_population) * 100 if total_population > 0 else 0
    women_share = (total_women / total_population) * 100 if total_population > 0 else 0

    largest_group_row = df_grouped_filtered.loc[df_grouped_filtered["pocet_spolu"].idxmax()]
    smallest_group_row = df_grouped_filtered.loc[df_grouped_filtered["pocet_spolu"].idxmin()]

    summary_table_tab1 = pd.DataFrame({
        "Ukazovateľ": [
            "Vek s najvyšším počtom obyvateľov",
            "Najstarší obyvateľ",
            "Priemerný vek",
            "Podiel mužov",
            "Podiel žien",
            "Najpočetnejšia veková skupina",
            "Najmenej početná veková skupina"
        ],
        "Hodnota": [
            f"{int(max_age_row['vek'])} rokov ({int(max_age_row['pocet_spolu']):,})".replace(",", " "),
            f"{int(oldest_row['vek'])} rokov ({int(oldest_row['pocet_spolu']):,})".replace(",", " "),
            f"{average_age:.1f} roka",
            f"{men_share:.2f} %",
            f"{women_share:.2f} %",
            f"{largest_group_row['vekova_skupina']} ({int(largest_group_row['pocet_spolu']):,})".replace(",", " "),
            f"{smallest_group_row['vekova_skupina']} ({int(smallest_group_row['pocet_spolu']):,})".replace(",", " ")
        ]
    })

    st.dataframe(summary_table_tab1, use_container_width=True, hide_index=True)
    st.markdown("---")
    st.caption("Zdroj dát: [Mesto Nitra - OPEN DATA](https://klient.nitra.sk/default.aspx?NavigationState=1100:0:)")

# =============================
# TAB 2 - VÝVOJ POPULÁCIE
# =============================
with tab2:
    st.header("Vývoj populácie")

    df_pop_filtered = df_pop[
        (df_pop["Rok"] >= selected_year_range[0]) &
        (df_pop["Rok"] <= selected_year_range[1])
        ].copy()

    fig5 = px.line(
        df_pop_filtered,
        x="Rok",
        y="Počet občanov spolu",
        labels={"Rok": "Rok", "Počet občanov spolu": "Počet obyvateľov"},
        title = "Vývoj počtu obyvateľov mesta Nitra"
    )
    st.plotly_chart(fig5, use_container_width=True, key="pop_total")



    fig6 = px.line(
        df_pop_filtered,
        x="Rok",
        y=["Počet mužov", "Počet žien"],
        labels={"Rok": "Rok", "value": "Počet osôb", "variable": "Pohlavie"},
        title = "Vývoj počtu mužov a žien"
    )
    st.plotly_chart(fig6, use_container_width=True, key="pop_gender")



    fig7 = px.bar(
        df_pop_filtered[df_pop_filtered["Rok"] != df_pop_filtered["Rok"].min()],
        x="Rok",
        y="Saldo",
        labels={"Rok": "Rok", "Saldo": "Saldo"},
        title ="Demografické saldo"
    )
    st.plotly_chart(fig7, use_container_width=True, key="pop_saldo")



    fig8 = px.line(
        df_pop_filtered[df_pop_filtered["Rok"] != df_pop_filtered["Rok"].min()],
        x="Rok",
        y="Zmena_%",
        labels={"Rok": "Rok", "Zmena_%": "Zmena (%)"},
        title="Percentuálna zmena populácie (%)"
    )
    st.plotly_chart(fig8, use_container_width=True, key="pop_change")


    st.markdown("---")
    st.subheader("Súhrnné štatistiky populácie")

    max_population_row = df_pop_filtered.loc[df_pop_filtered["Počet občanov spolu"].idxmax()]
    min_population_row = df_pop_filtered.loc[df_pop_filtered["Počet občanov spolu"].idxmin()]
    max_growth_row = df_pop_filtered.loc[df_pop_filtered["Zmena_%"].idxmax()]
    min_growth_row = df_pop_filtered.loc[df_pop_filtered["Zmena_%"].idxmin()]

    avg_population = df_pop_filtered["Počet občanov spolu"].mean()
    avg_change = df_pop_filtered["Zmena_%"].dropna().mean()
    avg_saldo = df_pop_filtered["Saldo"].dropna().mean()

    first_population = df_pop_filtered["Počet občanov spolu"].iloc[0]
    last_population = df_pop_filtered["Počet občanov spolu"].iloc[-1]
    total_change = last_population - first_population

    summary_table = pd.DataFrame({
        "Ukazovateľ": [
            "Rok s najvyšším počtom obyvateľov",
            "Rok s najnižším počtom obyvateľov",
            "Priemerný počet obyvateľov",
            "Priemerná percentuálna zmena (%)",
            "Priemerné saldo",
            "Celková zmena za sledované obdobie",
            "Najväčší medziročný rast (%)",
            "Najväčší medziročný pokles (%)"
        ],
        "Hodnota": [
            f"{int(max_population_row['Rok'])} ({int(max_population_row['Počet občanov spolu']):,})".replace(",", " "),
            f"{int(min_population_row['Rok'])} ({int(min_population_row['Počet občanov spolu']):,})".replace(",", " "),
            f"{avg_population:,.0f}".replace(",", " "),
            f"{avg_change:.2f} %",
            f"{avg_saldo:,.0f}".replace(",", " "),
            f"{total_change:,.0f}".replace(",", " "),
            f"{int(max_growth_row['Rok'])} ({max_growth_row['Zmena_%']:.2f} %)",
            f"{int(min_growth_row['Rok'])} ({min_growth_row['Zmena_%']:.2f} %)"
        ]
    })

    st.dataframe(summary_table, use_container_width=True, hide_index=True)
    st.markdown("---")
    st.caption("Zdroj dát: [Mesto Nitra - OPEN DATA](https://klient.nitra.sk/default.aspx?NavigationState=1100:0:)")

# =============================
# TAB 3 - Demografia podľa ulíc
# =============================
with tab3:
    st.header("Štatistika ulíc")

    df_street_filtered = df_street.copy()

    street_y_column = "spolu"
    street_y_label = "Počet obyvateľov"

    if street_metric == "Na trvalom pobyte":
        street_y_column = "trvaly_pobyt"
        street_y_label = "Počet obyvateľov s trvalým pobytom"
    elif street_metric == "Na prechodnom pobyte":
        street_y_column = "prechodny_pobyt"
        street_y_label = "Počet obyvateľov s prechodným pobytom"

    df_street_filtered = df_street.copy()

    df_street_top = df_street_filtered.sort_values(
        street_y_column, ascending=False
    ).head(top_n_streets)

    street_options = sorted(df_street["ulica"].dropna().unique().tolist())
    selected_street = st.session_state.get("selected_street", street_options[0] if street_options else None)




    fig_street_1 = px.bar(
        df_street_top.sort_values(street_y_column, ascending=True),
        x=street_y_column,
        y="ulica",
        orientation="h",
        labels={street_y_column: street_y_label, "ulica": "Ulica"},
        title=f"Top ulice podľa ukazovateľa: {street_y_label}"
    )
    st.plotly_chart(fig_street_1, use_container_width=True, key="street_top_chart")




    df_street_top_spolu = df_street.sort_values("spolu", ascending=False).head(top_n_streets).copy()

    street_order_spolu = df_street_top_spolu["ulica"].tolist()

    df_street_age = df_street_top_spolu.melt(
        id_vars="ulica",
        value_vars=["predproduktivny", "produktivny", "poproduktivny"],
        var_name="vekova_kategoria",
        value_name="pocet"
    )

    df_street_age["ulica"] = pd.Categorical(
        df_street_age["ulica"],
        categories=street_order_spolu,
        ordered=True
    )

    df_street_age["vekova_kategoria"] = df_street_age["vekova_kategoria"].replace({
        "predproduktivny": "Predproduktívny vek",
        "produktivny": "Produktívny vek",
        "poproduktivny": "Poproduktívny vek"
    })

    fig_street_2 = px.bar(
        df_street_age,
        x="pocet",
        y="ulica",
        color="vekova_kategoria",
        orientation="h",
        barmode="stack",
        category_orders={"ulica": street_order_spolu},
        labels={
            "ulica": "Ulica",
            "pocet": "Počet osôb",
            "vekova_kategoria": "Veková kategória"
        },
        title="Veková štruktúra na top uliciach podľa celkového počtu obyvateľov"
    )

    st.plotly_chart(fig_street_2, use_container_width=True, key="street_age_chart")
    st.subheader("Detail vybranej ulice")

    street_options_with_empty = [""] + street_options

    selected_street = st.selectbox(
        "Vyber ulicu",
        street_options_with_empty,
        key="selected_street"
    )

    if selected_street:
        street_detail = df_street[df_street["ulica"] == selected_street].iloc[0]

        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("Spolu", int(street_detail["spolu"]))
        with col5:
            st.metric("Muži", int(street_detail["muzi"]))
        with col6:
            st.metric("Ženy", int(street_detail["zeny"]))

        col7, col8, col9 = st.columns(3)
        with col7:
            st.metric("Trvalý pobyt", int(street_detail["trvaly_pobyt"]))
        with col8:
            st.metric("Prechodný pobyt", int(street_detail["prechodny_pobyt"]))
        with col9:
            st.metric("Produktívny vek", int(street_detail["produktivny"]))

        st.subheader("Pohlavie na vybranej ulici")

        street_gender_df = pd.DataFrame({
            "kategoria": ["Muži", "Ženy"],
            "pocet": [street_detail["muzi"], street_detail["zeny"]]
        })

        fig_street_3 = px.pie(
            street_gender_df,
            names="kategoria",
            values="pocet",
            title=f"Pohlavie na ulici {selected_street}"
        )
        st.plotly_chart(fig_street_3, use_container_width=True, key="street_gender_pie")

        st.subheader("Vekové kategórie na vybranej ulici")

        street_age_detail_df = pd.DataFrame({
            "kategoria": ["Predproduktívny vek", "Produktívny vek", "Poproduktívny vek"],
            "pocet": [
                street_detail["predproduktivny"],
                street_detail["produktivny"],
                street_detail["poproduktivny"]
            ]
        })

        fig_street_4 = px.bar(
            street_age_detail_df,
            x="kategoria",
            y="pocet",
            labels={"kategoria": "Kategória", "pocet": "Počet osôb"},
            title=f"Vekové kategórie na ulici {selected_street}"
        )
        st.plotly_chart(fig_street_4, use_container_width=True, key="street_age_detail_bar")

    else:
        st.info("Vyberte ulicu zo zoznamu, aby sa zobrazili podrobné informácie.")

    st.markdown("---")
    st.subheader("Súhrnné štatistiky ulíc")

    largest_street_row = df_street.loc[df_street["spolu"].idxmax()]
    smallest_street_row = df_street.loc[df_street["spolu"].idxmin()]
    largest_productive_row = df_street.loc[df_street["produktivny"].idxmax()]
    largest_permanent_row = df_street.loc[df_street["trvaly_pobyt"].idxmax()]

    largest_preproductive_row = df_street.loc[df_street["predproduktivny"].idxmax()]
    largest_postproductive_row = df_street.loc[df_street["poproduktivny"].idxmax()]

    average_population_street = df_street["spolu"].mean()
    total_streets = df_street["ulica"].nunique()

    productive_share = (
        df_street["produktivny"].sum() / df_street["spolu"].sum() * 100
        if df_street["spolu"].sum() > 0 else 0
    )

    summary_table_tab3 = pd.DataFrame({
        "Ukazovateľ": [
            "Počet ulíc v datasete",
            "Priemerný počet obyvateľov na ulicu",
            "Ulica s najvyšším počtom obyvateľov",
            "Ulica s najvyšším počtom obyvateľov v predproduktívnom veku",
            "Ulica s najvyšším počtom obyvateľov v poproduktívnom veku",
            "Podiel produktívneho veku zo všetkých obyvateľov"
        ],
        "Hodnota": [
            f"{total_streets}",
            f"{average_population_street:,.0f}".replace(",", " "),
            f"{largest_street_row['ulica']} ({int(largest_street_row['spolu']):,})".replace(",", " "),
            f"{largest_preproductive_row['ulica']} ({int(largest_preproductive_row['predproduktivny']):,})".replace(",", " "),
            f"{largest_postproductive_row['ulica']} ({int(largest_postproductive_row['poproduktivny']):,})".replace(",", " "),
            f"{productive_share:.2f} %"
        ]
    })

    st.dataframe(summary_table_tab3, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.caption("Zdroj dát: [Mesto Nitra - OPEN DATA](https://klient.nitra.sk/default.aspx?NavigationState=1100:0:)")

