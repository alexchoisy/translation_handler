# 3_Verifier_un_fichier_csv_(_AI_powered_).py

import json
import sys
import os
import time
import dotenv as denv

# Ajouter le répertoire contenant utils.py au sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(project_root, 'functions'))

from openai import OpenAI
import streamlit as st
from utils import enableDisable, merge_verified_translations, propose_translations_deepl, transform_json, verify_by_AI, verify_by_openAI
import numpy as np
import pandas as pd
import os
import zipfile
import base64
import xml.etree.ElementTree as ET
import xml.dom.minidom
import requests
# disable ssl warnings for dev purposes
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

denv.load_dotenv()

st.set_page_config(page_title="Vérifier un fichier CSV (AI powered)", page_icon="📂", layout="wide")

openAIAPIKey = os.getenv('OPENAI_API_KEY')
deepLAPIKEY = os.getenv('DEEPL_API_KEY')
baseUrl = os.getenv('OPENLLM_BASE_URL')

if "form_sending" not in st.session_state:
    st.session_state.form_sending = False

st.title('Vérifier un fichier CSV (AI powered)')

st.markdown(
    """
    Cette application permet de fournir un fichier csv contenant des labels auprès d'une IA pour en vérifier le contenu.\n
    Plusieurs modèles d'IA sont disponibles, via OpenAI ou via un service intranet.\n
    Les instructions de vérification sont les suivantes :\n
    - Une traduction ne doit pas être vide\n
    - Une traduction doit appartenir au lexique de la langue indiquée\n
    - Une traduction doit correspondre à la valeur source pour la langue indiquée\n
"""
)

mainTab, logTab = st.tabs(['🧠 Application', '🔨 Debug'])

with mainTab:
    # Champ pour indiquer le séparateur utilisé pour le fichier CSV
    separator = st.text_input('Entrez le séparateur utilisé pour le fichier CSV (par défaut ",") :', ',', disabled=st.session_state.form_sending)

    # Téléverser un fichier CSV
    csv_file = st.file_uploader('Téléverser un fichier CSV :', type='csv', disabled=st.session_state.form_sending)
    exampleSet = {
        "Key": ["label.test"],
        "Domain": ["messages"],
        "fr": ["Test FR"],
        "en": ["Test EN"],
        "es": ["Test ES"],
        "de": ["Test DE"]
    }
    with st.container():
        st.caption('Exemple de fichier CSV :')
        st.table(exampleSet)

    optIA = st.toggle('Utiliser un modèle IA pour détecter les erreurs de traductions', disabled=st.session_state.form_sending)
    if optIA:
        with st.container(border=True):
            selected_source = st.selectbox('Choisir une source :', [{"key":"fake","label":'POC Mode ( Fake IA verification )'}, {"key":"openai","label":'OpenAI API ( Internet )'}, {"key":"local", "label":"Serveur local"}], format_func=(lambda opt: opt["label"]), placeholder='Choisir une option', disabled=st.session_state.form_sending)

            if selected_source["key"] == 'fake':
                selected_model = 'fake'

            if selected_source["key"] == 'local':
                # Récupérer la liste des modèles disponibles depuis l'API Ollama
                response = requests.get(baseUrl+'tags', verify=False)
                models = response.json()['models']

                # Ajouter un sélecteur pour choisir un modèle d'IA
                selected_model = st.selectbox('Choisir un modèle d\'IA :', [model['name'] for model in models], disabled=st.session_state.form_sending)

            if selected_source["key"] == 'openai':
                client = OpenAI(api_key=openAIAPIKey)
                my_assistants = client.beta.assistants.list(
                    order="desc",
                    limit="20",
                )
                models = [
                    {
                        "type": "model",
                        "label": "gpt-4-turbo-preview",
                        "id": "gpt-4-turbo-preview"
                    },
                    {
                        "type": "model",
                        "label": "gpt-3.5-turbo-16k",
                        "id": "gpt-3.5-turbo-16k"
                    }
                ]
                for assistant in my_assistants.data:
                    models.append({
                        "type": "assistant",
                        "label": assistant.name,
                        "id": assistant.id
                    })

                selected_model = st.selectbox('Choisir un modèle d\'IA :', models, format_func=(lambda opt: opt["label"]+" ("+opt["type"]+ ")"), disabled=st.session_state.form_sending)

            # Ajouter un toggle pour les propositions deepL
            optDeepL = st.toggle('Utiliser DeepL pour proposer des corrections de traductions', disabled=st.session_state.form_sending)

    if st.button('Envoyer',on_click=enableDisable, args=("form_sending",True), disabled=st.session_state.form_sending) and csv_file:
        # Déclaration de la boite à logs
        logBox = logTab.expander(label='Logs', expanded=True)

        # Lire le fichier CSV
        df = pd.read_csv(csv_file, sep=separator)
        jsonVal = df.to_json()
        # Convertir jsonVal en dictionnaire
        jsonVal = json.loads(jsonVal)
        logBox.json(jsonVal, expanded=False)

        status = st.status("Transformation des données...", expanded=True)

        # Extraire les langues à partir des en-têtes du fichier CSV
        languages = df.columns[2:]
        targetLanguages = [lang for lang in languages if lang != 'fr']
        jsonTransformed = transform_json(jsonVal, 'fr', targetLanguages)

        logBox.code(jsonTransformed)
        time.sleep(1)

        status.write("Transformation des données  ✔️")
        logBox.json(jsonTransformed, expanded=False)

        if optIA and selected_model:
            status.update(label="Détection des lignes malformées...")

            if selected_source["key"] == 'fake':
                verified_translations = {
                    "label.admin": {
                        "source_fr": "Administration",
                        "translations": [
                        {
                            "target_language": "de",
                            "value": "Admin Konsole",
                            "output": "OK"
                        },
                        {
                            "target_language": "en",
                            "value": "Admin Console",
                            "output": "OK"
                        },
                        {
                            "target_language": "es",
                            "value": "Administración",
                            "output": "OK"
                        }
                        ]
                    },
                    "label.users": {
                        "source_fr": "Utilisateurs",
                        "translations": [
                        {
                            "target_language": "de",
                            "value": "Benutzer",
                            "output": "OK"
                        },
                        {
                            "target_language": "en",
                            "value": "Apples",
                            "output": "ERR: Incorrect translation"
                        },
                        {
                            "target_language": "es",
                            "value": "Usuarios",
                            "output": "OK"
                        }
                        ]
                    },
                    "label.referentiels": {
                        "source_fr": "Référentiels",
                        "translations": [
                        {
                            "target_language": "de",
                            "value": "Rahmenwerke",
                            "output": "OK"
                        },
                        {
                            "target_language": "en",
                            "value": "MemePasDeLanglais",
                            "output": "ERR: Invalid content"
                        },
                        {
                            "target_language": "es",
                            "value": "Referenciales",
                            "output": "OK"
                        }
                        ]
                    },
                    "label.organisations": {
                        "source_fr": "Organisations",
                        "translations": [
                        {
                            "target_language": "de",
                            "value": "",
                            "output": "ERR: Empty value"
                        },
                        {
                            "target_language": "en",
                            "value": "Organisations",
                            "output": "OK"
                        },
                        {
                            "target_language": "es",
                            "value": "",
                            "output": "ERR: Empty value"
                        }
                        ]
                    }
                }
                status.write("Détection des lignes malformées  ✔️")

            # Détecter les erreurs dans les lignes
            if selected_source["key"] == "local":
                verified_translations = verify_by_AI(jsonTransformed, baseUrl, selected_model)
                status.write("Détection des lignes malformées  ✔️")
                # st.json(verified_translations)

            # Tests openAI :
            if selected_source["key"] == "openai" and selected_model:
                verified_translations = verify_by_openAI(jsonTransformed, openAIAPIKey, selected_model)
                status.write("Détection des lignes malformées  ✔️")

            # st.write('WRITING JSON verified_translations')
            # st.json(verified_translations, expanded=False)

            df = merge_verified_translations(jsonVal, verified_translations, 'fr', targetLanguages)

            if optDeepL:
                status.update(label="Génération des propositions de traduction...")

                verified_translations = propose_translations_deepl(verified_translations, deepLAPIKEY, 'fr', targetLanguages)
                # st.write('Retour deepl :')
                # st.json(verified_translations, expanded=False)

                df = merge_verified_translations(jsonVal, verified_translations, 'fr', targetLanguages, True)

                status.write("Génération des propositions de traduction  ✔️")

        time.sleep(1)
        status.update(label="Terminé !", state="complete", expanded=True)

        # Afficher le contenu du fichier CSV sous forme de tableau
        st.write('Aperçu du fichier CSV :')
        st.write(df)

        enableDisable("form_sending", False)