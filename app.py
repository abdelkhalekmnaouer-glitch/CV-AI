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

RÈGLES IMPORTANTES :

1) Hook :
- Commence par "Candidat Stage PFE en"
- Maximum 20 mots
- Ton technique
- Pas marketing

2) Profil :
- Paragraphe professionnel
- Conserver identité mécanique / FEA / simulation

3) Compétences :
- Ne jamais supprimer les compétences existantes
- Ajouter uniquement les nouvelles pertinentes
- Ne pas répéter une compétence déjà existante
- Pas de doublon sémantique

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

    try:
        result_json = json.loads(content)
    except:
        st.error("Erreur parsing JSON")
        st.write(content)
        st.stop()

    # ======================
    # Injection dans template LaTeX
    # ======================

    with open("template.tex", "r", encoding="utf-8") as f:
        template = f.read()

    def unique_items(items):
        return list(dict.fromkeys(items))

    def build_items(items):
        latex_items = ""
        for item in unique_items(items):
            latex_items += f"\\item {item}\n"
        return latex_items

    add_structural = build_items(
        result_json["skills"].get("Analyse Structurale et Simulation", [])
    )

    add_software = build_items(
        result_json["skills"].get("Logiciels de Simulation", [])
    )

    add_programming = build_items(
        result_json["skills"].get("Programmation et Outils", [])
    )

    final_latex = template.replace("<<HOOK>>", result_json["hook"])
    final_latex = final_latex.replace("<<PROFILE>>", result_json["profile"])
    final_latex = final_latex.replace("<<ADD_STRUCTURAL>>", add_structural)
    final_latex = final_latex.replace("<<ADD_SOFTWARE>>", add_software)
    final_latex = final_latex.replace("<<ADD_PROGRAMMING>>", add_programming)

    st.subheader("Code LaTeX généré")
    st.code(final_latex, language="latex")

    st.download_button(
        "Télécharger le fichier .tex",
        final_latex,
        file_name="CV_MNAOUER_Abdelkhalek.tex"
    )
