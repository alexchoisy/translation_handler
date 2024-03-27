import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏡",
)

st.write("# Bienvenue sur l'application de gestion des traductions 🌍")

st.markdown(
    """
    Cette application dédiée à l'utilisation pour Arengibox permet de transformer des labels depuis le format XLIFF, utilisé par Symfony, vers un fichier CSV et inversement.

    **👈 Sélectionnez une application depuis la barre de gauche pour débuter ** 
"""
)