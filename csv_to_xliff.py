import streamlit as st
import pandas as pd
import os
import zipfile
import base64
import xml.etree.ElementTree as ET
import xml.dom.minidom

st.title('Convertir un fichier CSV en fichiers XLIFF')

# Téléverser un fichier CSV
csv_file = st.file_uploader('Téléverser un fichier CSV :', type='csv')
if csv_file:
    # Lire le fichier CSV
    df = pd.read_csv(csv_file)

    pivot_table = {}

    # Parcourir les lignes du fichier CSV et créer un fichier XLIFF par langue
    for index, row in df.iterrows():
        domain = row['Domain']
        key = row['Key']
        translations = row.drop(['Domain', 'Key'])

        # Ajouter la clé et la traduction au fichier XLIFF correspondant
        for lang, value in translations.items():
            filename = f"{domain}.{lang}.xliff"
            if filename not in pivot_table:
                pivot_table[filename] = {}
            pivot_table[filename][key] = value

    st.write('Pivot table : ')
    st.write(pivot_table)

    # Créer un dossier temporaire pour stocker les fichiers XLIFF
    temp_folder = 'temp_xliff_files'
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    xliff_files = {}

    # Créer un fichier XLIFF pour chaque clé de "pivot_table"
    for filename, translations in pivot_table.items():
        domain, lang = filename.split('.')[:-1]

        # Créer le squelette du fichier XLIFF
        xliff_root = ET.Element('xliff')
        xliff_root.attrib['version'] = '1.2'
        xliff_root.attrib['xmlns'] = 'urn:oasis:names:tc:xliff:document:1.2'

        file_element = ET.SubElement(xliff_root, 'file')
        file_element.attrib['original'] = f'{domain}.xliff'
        file_element.attrib['datatype'] = 'plaintext'
        file_element.attrib['source-language'] = 'en'
        file_element.attrib['target-language'] = lang

        body_element = ET.SubElement(file_element, 'body')

        # Ajouter les clés et les traductions au fichier XLIFF
        for key, value in translations.items():
            trans_unit_element = ET.SubElement(body_element, 'trans-unit')
            trans_unit_element.attrib['id'] = f'{domain}.{key}'

            source_element = ET.SubElement(trans_unit_element, 'source')
            source_element.text = key

            target_element = ET.SubElement(trans_unit_element, 'target')
            target_element.text = value

        xliff_files[filename] = (xliff_root, [])

    # Enregistrer les fichiers XLIFF dans le dossier temporaire
    for filename, (xliff_root, trans_units) in xliff_files.items():
        # Ajouter l'indentation XML
        rough_string = ET.tostring(xliff_root, 'utf-8')
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml()

        # Écrire le fichier XLIFF dans le dossier temporaire
        with open(f"{temp_folder}/{filename}", "w") as f:
            f.write(pretty_xml)

    # Créer une archive ZIP contenant tous les fichiers XLIFF
    zip_file = 'output.zip'
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, file)
            zipf.write(file_path, os.path.basename(file_path))

    # Convertir le fichier ZIP en chaîne de caractères encodée en base64
    with open(zip_file, "rb") as f:
        zip_content = base64.b64encode(f.read()).decode('utf-8')

    # Créer un lien de téléchargement pour le fichier ZIP
    download_link = f'<a href="data:application/zip;base64,{zip_content}" download="files.zip">Télécharger les fichiers XLIFF</a>'

    # Afficher le lien de téléchargement
    st.markdown(download_link, unsafe_allow_html=True)

    # Supprimer tous les fichiers dans le dossier temporaire
    for filename in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, filename)
        os.remove(file_path)

    # Supprimer le dossier temporaire
    os.removedirs(temp_folder)