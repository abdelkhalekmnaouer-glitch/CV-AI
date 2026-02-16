import streamlit as st
import subprocess
import json
import requests

st.title("Générateur CV Intelligent")

offer = st.text_area("Collez l'offre de stage ici")

if st.button("Générer CV"):

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
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    result = response.json()
    content = result["choices"][0]["message"]["content"]
    result_json = json.loads(content)

    with open("template.tex", "r", encoding="utf-8") as f:
        template = f.read()

    template = template.replace("<<HOOK>>", result_json["hook"])
    template = template.replace("<<PROFILE>>", result_json["profile"])

    skills_block = ""
    for category, items in result_json["skills"].items():
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
