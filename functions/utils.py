# utils.py

from functools import reduce
import time
import pandas as pd
import requests
import streamlit as st
import deepl
import json
from openai import OpenAI

def enableDisable(stateVar, boolVal=True):
    st.session_state[stateVar] = boolVal

def transform_json(jsonDict, baseLang, targetLangs):

    # Initialiser jsonTransformed comme un dictionnaire vide
    jsonTransformed = {}

    # Parcourir les lignes du tableau
    for i in range(len(jsonDict['Key'])):
        key = jsonDict['Key'][str(i)]
        source_fr = jsonDict[baseLang][str(i)]
        translations = []

        # Parcourir les langues
        for lang in targetLangs:
            value = jsonDict[lang][str(i)]
            translations.append({
                "target_language": lang,
                "value": value if value is not None else "",
                "output": ""
            })

        # Ajouter l'entrée au dictionnaire jsonTransformed
        jsonTransformed[key] = {
            "source_fr": source_fr,
            "translations": translations
        }

    # Convertir jsonTransformed en chaîne JSON
    return jsonTransformed

def merge_verified_translations(jsonVal, verified_translations, baseLang, targetLangs, deepl=False):
    
    # Convertir jsonVal en DataFrame
    df = pd.DataFrame(jsonVal)

    # Créer un DataFrame temporaire pour stocker les traductions vérifiées
    columns = ['Key', 'Output', 'Reason']
    if deepl:
        for lang in targetLangs:
            columns.append(f"deepl_{lang}")
    temp_df = pd.DataFrame(columns=columns)

    # Parcourir les clés du dictionnaire verified_translations
    for key in verified_translations:

        translations = verified_translations[key]['translations']
        outputTranslations = []
        outputReasons = []

        row = {
            'Key': key
        }

        # Ajouter chaque traduction au DataFrame temporaire
        for translation in translations:
            outputTranslations.append(translation['output'])
            if translation['output'] != "OK":
                lang = translation['target_language'].upper()
                outputReasons.append(translation['output'].replace("ERR:", f"{lang}:"))
                if deepl:
                    row[f"deepl_{lang.lower()}"] = translation[f"deepl_{lang.lower()}"]

        row['Output'] = reduce(lambda a, b: "OK" if a == "OK" and b == "OK" else "ERR", outputTranslations)
        row['Reason'] = ', '.join(outputReasons)

        temp_df = pd.concat([temp_df, pd.DataFrame(row, index=[0])])

    # Fusionner le DataFrame temporaire avec le DataFrame d'origine
    df = df.merge(temp_df, on=['Key'], how='left')

    return df

def verify_by_AI(translations, baseUrl, model):
    url = baseUrl+"generate"

    # Préparer les données pour la requête
    data = {
        "model": model,
        "system": "You are a helpful assistant, expert in translations that helps cleanup CSV files containing translations from French to other languages. The translations will be given in the following json format : {\"key\": {\"source_fr\": \"BASE\", \"translations\": [{\"target_language\": \"en\", \"value\": \"VALUE\", \"output\": \"\"}, {\"target_language\": \"es\", \"value\": \"VALUE\", \"output\": \"\"}, {\"target_language\": \"de\", \"value\": \"VALUE\", \"output\": \"\"}]}, ...}  \n BASE represents the French phrase to translate. Given the following rules for verification : VALUE must be filled and must contain at least one character, VALUE must match the target language, VALUE must be an accurate translation of the corresponding BASE from French to target language. Use those rules to fill \"output\" with OK when the value respects all the rules, or ERR: Reason when you detect an error. Do not change anything besides \"output\".",
        "format":"json",
        "stream": False   
    }

    jsonEncoded = json.dumps(translations)
        
    data["prompt"] = f"[INST]Please verify the following translations :\n{jsonEncoded}[/INST]"

    # Envoyer la requête POST à l'API Ollama
    response = requests.post(url, json=data, verify=False)

    # Extraire les réponses de l'API
    if response.status_code == 200:
        # assistant_responses = response.json()['message']['content'].split('\n\n')
        assistant_response = response.json()["response"]
        st.code(assistant_response)
        st.write(type(assistant_response))

        #return assistant_responses
        return assistant_response
    else:
        print(f"Error: Failed to get response from Ollama API. Status code: {response.status_code}")
        return [True] * len(translations)
    
def verify_by_openAI(translations, api_key, selected_model):
    # Configurer l'API OpenAI
    client = OpenAI(api_key=api_key)

    if selected_model["type"] == "model":
        # Préparer le message system
        system_message = (
            "You are a helpful assistant, expert in translations that helps cleanup "
            "CSV files containing translations from French to other languages. The "
            "translations will be given in the following json format : "
            "{\"key\": {\"source_fr\": \"BASE\", \"translations\": "
            "[{\"target_language\": \"en\", \"value\": \"VALUE\", \"output\": \"\"}, "
            "{\"target_language\": \"es\", \"value\": \"VALUE\", \"output\": \"\"}, "
            "{\"target_language\": \"de\", \"value\": \"VALUE\", \"output\": \"\"}], ...} "
            "BASE represents the French phrase to translate. Given the following rules for verification : "
            "VALUE must be filled and must contain at least one character, VALUE must match the target language, "
            "VALUE must be an accurate translation of the corresponding BASE from French to target language. "
            "Use those rules to fill \"output\" with OK when the value respects all the rules, or "
            "ERR: Reason when you detect an error. Do not change anything besides \"output\". Answer only in JSON"
        )

        # Préparer la requête pour l'API OpenAI
        messages = [{"role": "system", "content": system_message}]
        messages.append({"role": "user", "content": json.dumps(translations)})

        # Envoyer la requête à l'API OpenAI
        completion = client.chat.completions.create(model=selected_model["id"],messages=messages, response_format={"type":"json_object"})

        # Analyser la réponse de l'API OpenAI
        assistant_response = completion.choices[0].message.content
        parsed_response = json.loads(assistant_response)

        return parsed_response

    if selected_model["type"] == "assistant":
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=json.dumps(translations)
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=selected_model["id"],
            #instructions="Respond with a single JSON only. There will be no text or other characters outside the JSON string."
        )
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1) # Wait for 1 second
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            st.write(messages.data[0].content)
            st.write('FINAL RESPONSE ---------------------')
            # st.write(messages.data[0].content.text.value)
            return messages
        
def propose_translations_deepl(verified_translations, deepLAPIKEY, baseLang, targetLangs, logBox=None):
    # Initialiser l'API DeepL
    auth_key = deepLAPIKEY
    translator = deepl.Translator(auth_key)

    err_translations = {lang: [] for lang in targetLangs}

    # Parcourir les traductions vérifiées
    for key in verified_translations:
        translations = verified_translations[key]['translations']

        # Regrouper les traductions contenant un output différent de "OK" par "target_language"
        for i, translation in enumerate(translations):
            if translation['output'] != "OK":
                err_translations[translation['target_language']].append({
                    "key": key,
                    "source": verified_translations[key]["source_fr"],
                    "index": i
                })

    # Utiliser l'API de DeepL pour traduire ces éléments (max 50 traductions à la fois)
    for lang, translations_to_send in err_translations.items():
        for i in range(0, len(translations_to_send), 50):
            chunk = translations_to_send[i:i+50]
            source_texts = [t['source'] for t in chunk]
            result = translator.translate_text(source_texts, source_lang=baseLang, target_lang=("EN-US" if lang.upper() == "EN" else lang), tag_handling="html", preserve_formatting=True)
            
            # st.write('DEEPL OUTPUT')
            # st.write(result)

            # Mettre à jour les traductions vérifiées avec les nouvelles traductions proposées
            for j, t in enumerate(chunk):
                propKey = f"deepl_{lang}"
                verified_translations[t['key']]['translations'][t['index']][propKey] = result[j].text

    return verified_translations