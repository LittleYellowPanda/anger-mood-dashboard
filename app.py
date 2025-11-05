import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text  
from io import BytesIO

# ---------- Configuration ----------
st.set_page_config(page_title="Évaluation Colère et Humeur", layout="centered")
DB_PATH = "sqlite:///data.db"
engine = create_engine(DB_PATH)

# ---------- Initialisation ----------
st.title("🧠 Questionnaire : Colère et Humeur (DAS & PANAS)")

# Crée la table si elle n’existe pas
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            das_scores TEXT,
            panas_scores TEXT,
            das_total INTEGER,
            pa_total INTEGER,
            na_total INTEGER
        )
    """))
    conn.commit()

# ---------- Fonctions ----------
def compute_scores(das, panas):
    das_total = sum(das.values())

    # PANAS : indices selon ta grille
    pa_items = [1, 3, 5, 9, 10, 12, 14, 16, 17, 19]
    na_items = [2, 4, 6, 7, 8, 11, 13, 15, 18, 20]
    pa_total = sum(panas[i] for i in pa_items)
    na_total = sum(panas[i] for i in na_items)
    return das_total, pa_total, na_total

# ---------- FORMULAIRE ----------
with st.form("questionnaire"):
    st.subheader("🚗 Partie 1 : Échelle de Colère au Volant (DAS)")
    st.text("Il s'agit d'une échelle de 1 à 5: 1 => plus faible intensité de colère. 5 => plus forte intensité de colère.")
    das = {}
    das_questions = [
        "Quelqu'un zigzag entre les voies de circulation.",
        "Un véhicule lent refuse de se rabattre.",
        "Quelqu'un recule devant vous sans regarder.",
        "Quelqu'un ne s'arrête pas à un feu rouge.",
        "Vous passez devant un radar.",
        "Quelqu'un accélère lorsque vous tentez de dépasser.",
        "Quelqu'un est lent à se garer et bloque la circulation.",
        "Vous êtes bloqué(e) dans un embouteillage.",
        "Quelqu'un vous fait un geste obscène.",
        "Quelqu'un vous klaxonne.",
        "Un cycliste roule au milieu de la voie.",
        "Un policier vous arrête.",
        "Un camion projette du gravier sur votre voiture.",
        "Vous ne pouvez pas voir au-delà d’un camion."
    ]
    for i, q in enumerate(das_questions, 1):
        das[i] = st.radio(q, [1, 2, 3, 4, 5], horizontal=True)

    st.subheader("😊 Partie 2 : Échelle d’Affect Positif et Négatif (PANAS)")
    panas = {}
    panas_items = [
        "Intéressé(e)", "Perturbé(e)", "Excité(e)", "Bouleversé(e)",
        "Fort(e)", "Coupable", "Effrayé(e)", "Hostile", "Enthousiaste",
        "Fier(ère)", "Irritable", "Alerte", "Honteux(se)", "Inspiré(e)",
        "Nerveux(se)", "Déterminé(e)", "Attentif(ve)", "Agité(e)", "Actif(ve)", "Craintif(ve)"
    ]
    for i, emotion in enumerate(panas_items, 1):
        panas[i] = st.radio(emotion, [1, 2, 3, 4, 5], horizontal=True)

    submitted = st.form_submit_button("✅ Soumettre mes réponses")

# ---------- TRAITEMENT ----------
if submitted:
    das_total, pa_total, na_total = compute_scores(das, panas)

    # Sauvegarde
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO responses (das_scores, panas_scores, das_total, pa_total, na_total) VALUES (:das, :panas, :das_total, :pa_total, :na_total)"),
            {"das": str(das), "panas": str(panas), "das_total": das_total, "pa_total": pa_total, "na_total": na_total}
        )
        conn.commit()

    st.success("✅ Réponses enregistrées avec succès !")

    st.write("### Vos Scores")
    st.metric("Score de Colère (DAS)", das_total)
    st.metric("Affect Positif (PA)", pa_total)
    st.metric("Affect Négatif (NA)", na_total)

# ---------- DASHBOARD ----------
st.markdown("---")
st.header("📊 Tableau de bord (résultats cumulés)")

if st.button("Actualiser les données"):
    df = pd.read_sql("SELECT * FROM responses", engine)
    st.dataframe(df)
    st.bar_chart(df[["das_total", "pa_total", "na_total"]])

# ---------- EXPORT ----------
st.markdown("### 📥 Exporter les réponses")
if st.button("Télécharger les réponses en CSV"):
    df = pd.read_sql("SELECT * FROM responses", engine)

    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Télécharger le fichier CSV",
            data=csv,
            file_name="responses.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Aucune donnée à exporter.")
