import streamlit as st
import json
import requests

st.title("Générateur CV LaTeX Intelligent")

offer = st.text_area("Collez l'offre de stage ici")

if st.button("Générer le code LaTeX"):

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
    # Injection dans template
    # ======================

    with open("template.tex", "r", encoding="utf-8") as f:
        template = f.read()

    # Construire bloc compétences LaTeX
    skills_block = ""
    for category, items in result_json["skills"].items():
        skills_block += f"\\noindent \\textbf{{{category}}}\n"
        skills_block += "\\begin{itemize}\n"
        for item in items:
            skills_block += f"\\item {item}\n"
        skills_block += "\\end{itemize}\n\n"

    final_latex = template.replace("<<HOOK>>", result_json["hook"])
    final_latex = final_latex.replace("<<PROFILE>>", result_json["profile"])
    final_latex = final_latex.replace("<<SKILLS_BLOCK>>", skills_block)

    st.subheader("Code LaTeX généré")
    st.code(final_latex, language="latex")

    st.download_button(
        "Télécharger le fichier .tex",
        final_latex,
        file_name="CV_MNAOUER_Abdelkhalek.tex"
    )
