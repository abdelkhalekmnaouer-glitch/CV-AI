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

OBJECTIF :
Adapter uniquement :
- Phrase d'accroche (hook)
- Profil
- Compétences

Ne modifier aucune autre section.

RÈGLES IMPORTANTES :

1) HOOK :
- Doit commencer par : "Candidat Stage PFE en"
- Maximum 20 mots
- Ton technique
- Pas marketing
- Pas de phrase entreprise

2) PROFIL :
- Paragraphe unique
- Conserver l'identité mécanique / FEA / simulation
- Intégrer les mots-clés pertinents
- Ne pas transformer en annonce RH

3) COMPÉTENCES :
- Ne jamais supprimer les compétences existantes
- Ne jamais répéter une compétence déjà existante
- Si une compétence existe déjà (ex : FEA = MEF), ne pas la réécrire
- Fusionner sans duplication
- Conserver absolument :
    - FEA / MEF
    - Analyse statique et dynamique
    - NVH
    - Abaqus / ANSYS / NASTRAN
    - Python / MATLAB
- Ajouter uniquement les compétences pertinentes de l’offre

4) Éviter les doublons sémantiques :
Exemples :
- FEA = MEF
- CATIA V5 déjà présent → ne pas répéter
- Python déjà présent → ne pas répéter

Offre :
{offer}

Retourner STRICTEMENT ce JSON :

{{
  "hook": "Candidat Stage PFE en ...",
  "profile": "Paragraphe professionnel adapté",
  "skills": {{
      "Analyse Structurale et Simulation": ["..."],
      "Logiciels de Simulation": ["..."],
      "Programmation et Outils": ["..."]
  }}
}}

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


