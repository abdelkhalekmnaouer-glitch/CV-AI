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
    Adapter uniquement :
    - Phrase d'accroche (HOOK)
    - Profil
    - Compétences

    Ne modifier aucune autre section.

    Offre :
    {offer}

    Retourner uniquement un JSON valide :

    {{
      "hook": "...",
      "profile": "...",
      "skills": {{
          "Analyse Structurale et Simulation": [...],
          "Logiciels de Simulation": [...],
          "Programmation et Outils": [...]
      }}
    }}
    """

    data = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ]
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
        st.error("Réponse inattendue")
        st.write(result)
        st.stop()

    content = result["choices"][0]["message"]["content"]

    try:
        result_json = json.loads(content)
    except:
        st.error("Erreur parsing JSON")
        st.write(content)
        st.stop()

    # ======================
    # GÉNÉRATION PDF SIMPLE
    # ======================

    pdf_text = f"""
ABDELKHALEK MNAOUER

{result_json["hook"]}

PROFIL
{result_json["profile"]}

COMPÉTENCES
"""

    for category, items in result_json["skills"].items():
        pdf_text += f"\n{category}\n"
        for item in items:
            pdf_text += f"- {item}\n"

    buffer = BytesIO()
    buffer.write(pdf_text.encode("utf-8"))
    buffer.seek(0)

    st.download_button(
        "Télécharger le CV",
        buffer,
        file_name="CV_MNAOUER_Abdelkhalek.txt"
    )

