import streamlit as st
import json
import requests

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
Tu es expert ATS pour ingénieur mécanique.

Règles :
- Hook commence par "Candidat Stage PFE en"
- Max 20 mots
- Ton technique
- Conserver FEA, MEF, NVH, Abaqus, ANSYS, Python
- Ajouter compétences pertinentes sans duplication

Offre :
{offer}

Retourner JSON strict :
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
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    result = response.json()

    if "choices" not in result:
        st.error("Erreur API")
        st.write(result)
        st.stop()

    content = result["choices"][0]["message"]["content"]
    result_json = json.loads(content)

    # ======================
    # TEMPLATE HTML
    # ======================

    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial;
                margin: 50px;
            }}
            h1 {{
                font-size: 22px;
                margin-bottom: 5px;
            }}
            h2 {{
                border-bottom: 1px solid black;
                font-size: 16px;
                margin-top: 25px;
            }}
            ul {{
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>

    <h1>ABDELKHALEK MNAOUER</h1>
    <p>{result_json["hook"]}</p>

    <h2>PROFIL</h2>
    <p>{result_json["profile"]}</p>

    <h2>COMPÉTENCES</h2>
    """

    for category, items in result_json["skills"].items():
        html += f"<h3>{category}</h3><ul>"
        for item in items:
            html += f"<li>{item}</li>"
        html += "</ul>"

    html += "</body></html>"

    st.components.v1.html(html, height=600, scrolling=True)

    st.download_button(
        "Télécharger en HTML (exportable en PDF)",
        html,
        file_name="CV_MNAOUER_Abdelkhalek.html"
    )
