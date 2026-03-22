import streamlit as st

st.set_page_config(
    page_title="Otvorené dáta mesta Nitra",
    page_icon="📊",
    layout="wide"
)

st.title("Analýza otvorených dát mesta Nitra")

st.write("""
Táto aplikácia slúži na vizualizáciu vybraných otvorených dát mesta Nitra.


Aplikácia obsahuje tri hlavné časti:
- Demografia mesta
- Rozpočet mesta
- Kvalita ovzdušia
""")

st.info("Vyberte sekciu v ľavom menu.")

with st.sidebar:
    st.title("Nitra Open Data")
    dataset = st.selectbox(
        "Vyber dataset",
        ["Demografia", "Rozpočet", "Ovzdušie"]
    )