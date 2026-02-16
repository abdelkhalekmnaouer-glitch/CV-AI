import streamlit as st
import json
import requests
from io import BytesIO

st.title("Générateur CV Intelligent")

offer = st.text_area("Collez l'offre de stage ici")

if st.button("Générer CV"):

    if not offer.strip():
        st.warning("Veuillez coller une offre.")
        st.stop()

    api_key = st.secrets["GROQ_API_KEY"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Tu es expert en optimisation ATS pour ingénieur mécanique.

IMPORTANT :
- Ne jamais supprimer les compétences existantes du candidat.
- Ajouter uniquement les compétences pertinentes de l’offre.
- Conserver son socle technique (FEA, MEF, NVH, Abaqus, ANSYS, etc.).
- Fusionner intelligemment les compétences existantes + celles de l’offre.
- Ne jamais transformer le profil en annonce RH.
- Le hook doit être professionnel, orienté candidature, pas marketing.

Offre :
{offer}

Générer STRICTEMENT ce JSON :

{{
  "hook": "Phrase d'accroche professionnelle adaptée à l'offre",
  "profile": "Paragraphe professionnel cohérent conservant l'identité mécanique et simulation du candidat, en intégrant les mots-clés de l'offre",
  "skills": {{
      "Analyse Structurale et Simulation": [
          "Conserver compétences existantes + ajouter pertinentes"
      ],
      "Logiciels de Simulation": [
          "Conserver existant + ajouter CATIA V5 si pertinent"
      ],
      "Programmation et Outils": [
          "Conserver Python, MATLAB etc + ajouter VB.NET si pertinent"
      ]
  }}
}}

Ne jamais supprimer :
- FEA / MEF
- Analyse statique/dynamique
- NVH
- Abaqus / ANSYS / Nastran
- Python

Ne rien écrire avant ou après le JSON.
"""

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        st.error("Erreur API Groq")
        st.write(response.text)
        st.stop()

    result = response.json()

    if "choices" not in result:
        st.error("Réponse inattendue de Groq")
        st.write(result)
        st.stop()

    content = result["choices"][0]["message"]["content"]

    try:
        result_json = json.loads(content)
    except:
        st.error("Le modèle n'a pas renvoyé un JSON valide.")
        st.write(content)
        st.stop()

    # ======================
    # GÉNÉRATION FICHIER TEXTE STABLE
    # ======================

    cv_text = f"""
ABDELKHALEK MNAOUER

{result_json["hook"]}

PROFIL
{result_json["profile"]}

COMPÉTENCES
"""

    for category, items in result_json["skills"].items():
        cv_text += f"\n{category}\n"
        for item in items:
            cv_text += f"- {item}\n"

    buffer = BytesIO()
    buffer.write(cv_text.encode("utf-8"))
    buffer.seek(0)

    st.download_button(
        "Télécharger le CV",
        buffer,
        file_name="CV_MNAOUER_Abdelkhalek.txt"
    )

