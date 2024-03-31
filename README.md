# translation_handler

Application permettant d'extraire les traductions XLIFF.

Ancienne version PHP : index.php

Nouvelle version écrite en python : Home.py

## Version python 

### Fonctionnalités
Importer un fichier CSV contenant des labels traduits dans différentes langues
Détecter les erreurs de traduction en utilisant une IA (modèles locaux ou OpenAI)
Regrouper les erreurs de traduction par langue cible
Proposer des corrections de traduction à l'aide de l'API de DeepL
Afficher les résultats sous forme de tableau et de JSON
Prérequis
Python 3.x
Streamlit
deepl
openai (optionnel)
Installation
Cloner le référentiel :

git clone https://github.com/votre-utilisateur/translation-handler.git
Installer les dépendances :

pip install -r requirements.txt
Configurer les clés d'API pour DeepL et OpenAI (optionnel) :

```# Dans 3_Fournir_un_csv_a_une_IA.py
deepLAPIKEY = "votre_cle_deepL"
openAIAPIKey = "votre_cle_openAI"```

Utilisation
Lancer l'application :

streamlit run 3_Fournir_un_csv_a_une_IA.py
Importer un fichier CSV contenant des labels traduits dans différentes langues
Choisir une source d'IA pour la détection des erreurs de traduction (locale ou OpenAI)
Optionnel : choisir un modèle d'IA pour la détection des erreurs de traduction
Optionnel : activer l'utilisation de DeepL pour proposer des corrections de traduction
Cliquer sur "Envoyer" pour traiter le fichier CSV
Afficher les résultats sous forme de tableau et de JSON
Remarques
L'application est conçue pour fonctionner avec des fichiers CSV ayant une structure spécifique, où les colonnes représentent les langues et les lignes représentent les labels traduits.
L'application prend en charge la détection d'erreurs de traduction en utilisant des modèles d'IA locaux ou OpenAI.
L'utilisation de l'API de DeepL pour proposer des corrections de traduction est optionnelle et peut être activée ou désactivée selon les besoins.