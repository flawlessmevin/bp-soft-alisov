import streamlit as st

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

st.title("Analýza otvorených dát mesta Nitra")

st.write("""
Táto aplikácia slúži na vizualizáciu a prehlad otvorených dát mesta Nitra.


Aplikácia obsahuje hlavné časti:
- Demografia mesta
- Rozpočet mesta
""")

with st.spinner("Načítavajú sa dáta aplikácie..."):
    load_population_data()
    load_street_data()
    load_orders_data()
    load_debtors_data()
    load_age_data()
    load_budget_data()

st.success("Dáta boli načítané.")


with st.sidebar:
    st.title("Nitra Open Data")


