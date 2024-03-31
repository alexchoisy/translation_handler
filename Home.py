import streamlit as st
import json

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

jsonVal = {
    "label.users": {
        "source_fr": "Utilisateurs",
        "translations" : [
            {"target_language": "en", "value": "Users", "output": ""},
            {"target_language": "es", "value": "", "output": ""},
            {"target_language": "de", "value": "Benutzer", "output": ""},
        ]
    },
    
    "label.admin": {
        "source_fr": "Administration",
        "translations" : [
            {"target_language": "en", "value": "Rienavoir", "output": ""},
            {"target_language": "es", "value": "Administration", "output": ""},
            {"target_language": "de", "value": "Arrivederzen", "output": ""},
        ]
    },
    "label.referentiels": {
        "source_fr": "Référentiels",
        "translations" : [
            {"target_language": "en", "value": "Frameworks", "output": ""},
            {"target_language": "es", "value": "Referenciales", "output": ""},
            {"target_language": "de", "value": "Administration", "output": ""},
        ]
    },
    "label.organisations": {
        "source_fr": "Organisations",
        "translations" : [
            {"target_language": "en", "value": "Organisations", "output": ""},
            {"target_language": "es", "value": "Organización(es)", "output": ""},
            {"target_language": "de", "value": "Orgganisationen", "output": ""},
        ]
    }
}

st.code(json.dumps(json.dumps(jsonVal)))
