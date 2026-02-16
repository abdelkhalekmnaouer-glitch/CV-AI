import streamlit as st
import json
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
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
        "model": "llama3-70b-8192",
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
        st.error("Réponse inattendue de Groq")
        st.write(result)
        st.stop()

    content = result["choices"][0]["message"]["content"]

    try:
        result_json = json.loads(content)
    except:
        st.error("Erreur JSON généré par le modèle")
        st.write(content)
        st.stop()

    # =====================
    # GÉNÉRATION PDF PYTHON
    # =====================

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    title_style = styles["Heading1"]

    elements.append(Paragraph("ABDELKHALEK MNAOUER", title_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(result_json["hook"], normal))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>PROFIL</b>", normal))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(result_json["profile"], normal))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>COMPÉTENCES</b>", normal))
    elements.append(Spacer(1, 6))

    for category, items in result_json["skills"].items():
        elements.append(Paragraph(f"<b>{category}</b>", normal))
        elements.append(Spacer(1, 4))
        bullet_points = [ListItem(Paragraph(item, normal)) for item in items]
        elements.append(ListFlowable(bullet_points, bulletType='bullet'))
        elements.append(Spacer(1, 8))

    doc.build(elements)

    st.download_button(
        "Télécharger le CV",
        buffer.getvalue(),
        file_name="CV_MNAOUER_Abdelkhalek.pdf"
    )
