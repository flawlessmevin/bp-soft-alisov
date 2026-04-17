import streamlit as st
import pandas as pd
import io


from data_loader import (
    load_orders_data,
    load_population_data,
    load_debtors_data,
    load_street_data,
    load_age_data,
    load_budget_data
)

st.set_page_config(
    page_title="Otvorené dáta mesta Nitra",
    page_icon="📊",
    layout="wide"
)

st.title("Nitra Open Data")
st.write(
    """
    Webová aplikácia zameraná na vizualizáciu vybraných otvorených dát mesta Nitra.
    Aplikácia obsahuje dve hlavné sekcie: **Demografia** a **Rozpočet**.
    """
)

with st.spinner("Načítavajú sa dáta aplikácie..."):
    df_population = load_population_data()
    df_street = load_street_data()
    df_orders = load_orders_data()
    df_debtors = load_debtors_data()
    df_age = load_age_data()
    df_budget = load_budget_data()

latest_population_row = df_population.sort_values("Rok").iloc[-1]
latest_population_total = latest_population_row["Počet občanov spolu"]

oldest_row = df_age.loc[df_age["vek"].idxmax()]
top_street_row = df_street.loc[df_street["spolu"].idxmax()]

average_efficiency = df_budget["Efektivita"].mean()

df_debtors_nitra = df_debtors[
    df_debtors["mesto"].astype(str).str.strip().str.lower() == "nitra"
].copy()
df_debtors_nitra["nedoplatok"] = pd.to_numeric(
    df_debtors_nitra["nedoplatok"], errors="coerce"
).fillna(0)
max_debtor_row = df_debtors_nitra.loc[df_debtors_nitra["nedoplatok"].idxmax()]

top_suppliers_count = (
    df_orders.groupby("dodavatel", as_index=False)
    .size()
    .rename(columns={"size": "pocet_objednavok"})
    .sort_values("pocet_objednavok", ascending=False)
)
top_supplier_count_row = top_suppliers_count.iloc[0]

summary_table_home = pd.DataFrame({
    "Ukazovateľ": [
        "Počet obyvateľov",
        "Najvyšší vek obyvateľa",
        "Ulica s najvyšším počtom obyvateľov",
        "Priemerná efektívnosť hospodárenia",
        "Najväčší daňový dlh v Nitre",
        "Dodávateľ s najvyšším počtom objednávok"
    ],
    "Hodnota": [
        f"{latest_population_total:,.0f}".replace(",", " "),
        f"{int(oldest_row['vek'])} rokov ({int(oldest_row['pocet_spolu']):,})".replace(",", " "),
        f"{top_street_row['ulica']} ({int(top_street_row['spolu']):,})".replace(",", " "),
        f"{average_efficiency:.2f} %",
        f"{max_debtor_row['nedoplatok']:,.2f} € ({max_debtor_row['dlznik']})".replace(",", " "),
        f"{top_supplier_count_row['dodavatel']} ({int(top_supplier_count_row['pocet_objednavok'])})"
    ]
})

st.markdown("---")
st.subheader("Súhrnné informácie")
st.dataframe(summary_table_home, use_container_width=True, hide_index=True)


st.markdown("---")
st.subheader("Sekcie aplikácie:")

col3, col4 = st.columns(2)

with col3:
    st.markdown(
        """
        ### Demografia

        Sekcia obsahuje vizualizácie vývoja populácie,
        vekovej štruktúry obyvateľov a demografie podľa ulíc.
        """
    )

with col4:
    st.markdown(
        """
        ### Rozpočet

        Sekcia obsahuje prehľad prehľad príjmov a výdavkov mesta, faktúry dodávateľov, a daňových dlžníkov.
        """
    )

st.markdown("---")
st.caption("Zdroj dát: [Mesto Nitra - OPEN DATA](https://klient.nitra.sk/default.aspx?NavigationState=1100:0:)")

with st.sidebar:
    st.title("Nitra Open Data")