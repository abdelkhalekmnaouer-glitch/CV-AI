import streamlit as st
import subprocess
import json
from openai import OpenAI

st.title("Générateur CV Intelligent")

offer = st.text_area("Collez l'offre de stage ici")

if st.button("Générer CV"):

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    result = json.loads(response.choices[0].message.content)

    with open("template.tex", "r", encoding="utf-8") as f:
        template = f.read()

    template = template.replace("<<HOOK>>", result["hook"])
    template = template.replace("<<PROFILE>>", result["profile"])

    skills_block = ""

    for category, items in result["skills"].items():
        skills_block += f"\\noindent \\textbf{{{category}}}\n"
        skills_block += "\\begin{itemize}\n"
        for item in items:
            skills_block += f"\\item {item}\n"
        skills_block += "\\end{itemize}\n\n"

    template = template.replace("<<SKILLS_BLOCK>>", skills_block)

    with open("final.tex", "w", encoding="utf-8") as f:
        f.write(template)

    subprocess.run(["pdflatex", "final.tex"])

    with open("final.pdf", "rb") as f:
        st.download_button(
            "Télécharger le CV",
            f,
            file_name="CV_MNAOUER_Abdelkhalek.pdf"
        )
