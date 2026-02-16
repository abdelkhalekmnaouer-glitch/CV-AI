import streamlit as st
import json
import requests
from fpdf import FPDF
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
    # GÉNÉRATION PDF AVEC FPDF
    # ======================

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ABDELKHALEK MNAOUER", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, result_json["hook"])
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "PROFIL", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, result_json["profile"])
    pdf.ln(3)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "COMPETENCES", ln=True)

    pdf.set_font("Arial", "", 11)

    for category, items in result_json["skills"].items():
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, category, ln=True)

        pdf.set_font("Arial", "", 11)
        for item in items:
            pdf.multi_cell(0, 6, f"- {item}")
        pdf.ln(2)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    st.download_button(
        "Télécharger le CV",
        buffer,
        file_name="CV_MNAOUER_Abdelkhalek.pdf"
    )
