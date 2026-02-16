import streamlit as st
import json
import requests

st.set_page_config(layout="centered")
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
    # DESIGN HTML PROFESSIONNEL
    # ======================

    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.5;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .name {{
                font-size: 22px;
                font-weight: bold;
            }}
            .hook {{
                font-size: 14px;
                margin-top: 5px;
            }}
            .section {{
                margin-top: 25px;
            }}
            .section-title {{
                font-weight: bold;
                border-bottom: 1px solid #000;
                margin-bottom: 8px;
                font-size: 14px;
            }}
            ul {{
                margin: 5px 0 10px 15px;
            }}
        </style>
    </head>
    <body>

    <div class="header">
        <div class="name">ABDELKHALEK MNAOUER</div>
        <div class="hook">{result_json["hook"]}</div>
    </div>

    <div class="section">
        <div class="section-title">PROFIL</div>
        <div>{result_json["profile"]}</div>
    </div>

    <div class="section">
        <div class="section-title">COMPÉTENCES</div>
    """

    for category, items in result_json["skills"].items():
        html += f"<strong>{category}</strong><ul>"
        for item in items:
            html += f"<li>{item}</li>"
        html += "</ul>"

    html += """
    </div>
    </body>
    </html>
    """

    st.components.v1.html(html, height=700, scrolling=True)

    st.download_button(
        "Télécharger en HTML (Exporter ensuite en PDF via Ctrl+P)",
        html,
        file_name="CV_MNAOUER_Abdelkhalek.html"
    )
