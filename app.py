import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ---------- Configuration ----------
st.set_page_config(page_title="Évaluation de la Conduite – DAS & DBQ", layout="centered")
DB_PATH = "sqlite:///data.db"
engine = create_engine(DB_PATH)

# ---------- Initialisation ----------
st.title("🚗 Questionnaire : Colère au Volant (DAS) & Comportements de Conduite (DBQ)")

# Crée la table si elle n’existe pas
# Ensure the table exists
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            gender TEXT,
            age INTEGER,
            education TEXT,
            driving_experience INTEGER,
            driving_time INTEGER,
            traffic_light_pref TEXT,
            das_total REAL,
            dbq_violations REAL,
            dbq_errors REAL,
            dbq_lapses REAL
        )
    """))
    conn.commit()

# ---------- Fonctions ----------
def compute_dbq_scores(dbq):
    # ✅ Adjusted indices for DBQ-28 short version
    violations_items = [4, 5, 7, 16, 18, 19, 21, 26, 27]
    errors_items = [9, 11, 12, 20, 24, 25, 28]
    lapses_items = [1, 2, 3, 6, 8, 10, 13, 14, 15, 17, 22, 23]

    violations = sum(dbq.get(i, 0) for i in violations_items)
    errors = sum(dbq.get(i, 0) for i in errors_items)
    lapses = sum(dbq.get(i, 0) for i in lapses_items)
    return violations, errors, lapses


# ---------- FORMULAIRE ----------
with st.form("questionnaire"):

    # === Partie 0 : Données démographiques ===
    st.subheader("👤 Partie 0 : Informations générales")

    gender = st.selectbox("Genre", ["Femme", "Homme", "Autre / Préfère ne pas dire"])
    age_group = st.selectbox("Âge", ["18–23", "24–34", "35–45", "46–60", "Plus de 60"])
    education = st.selectbox("Niveau d'études", [
        "Collège ou moins", "Lycée / École professionnelle",
        "BTS / DUT", "Licence", "Master ou plus"
    ])
    driving_experience = st.selectbox("Expérience de conduite", [
        "Moins d’1 an", "1–5 ans", "5–10 ans", "10–20 ans", "Plus de 20 ans"
    ])
    weekly_time = st.selectbox("Temps moyen de conduite hebdomadaire", [
        "Moins de 5 h", "5–20 h", "20–40 h", "40–60 h", "Plus de 60 h"
    ])
    reminder_method = st.selectbox(
        "Méthode de rappel du compte à rebours du feu de signalisation préférée",
        ["Audio (ex. annonce vocale)", "Visuelle (texte, écran)", "Tactile (vibration)",
         "Combinée (plusieurs méthodes)", "Autre"]
    )
    reminder_content = st.selectbox(
        "Contenu préféré du rappel de compte à rebours",
        ["Secondes restantes", "État du feu", "Vitesse recommandée", "Autre"]
    )

    # === Partie 1 : DAS ===
    st.subheader("😠 Partie 1 : Échelle de Colère au Volant (DAS)")
    st.caption("Échelle de 1 à 5 : 1 = Pas du tout en colère → 5 = Très en colère")

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

    # === Partie 2 : DBQ-28 ===
    st.subheader("🧠 Partie 2 : Questionnaire sur les Comportements de Conduite (DBQ-28)")
    st.caption("Échelle de 1 à 6 : 1 = Jamais → 6 = Presque tout le temps")

    dbq = {}
    dbq_items = [
        "1. Tenter de démarrer à un feu en troisième vitesse.",
        "2. Découvrir que vous roulez plus vite que la limite sans vous en rendre compte.",
        "3. Vous enfermer hors de la voiture avec les clés à l’intérieur.",
        "4. Dépasser un conducteur lent par la droite (voie intérieure).",
        "5. Conduire aussi vite sur route de campagne avec les feux de croisement qu’avec les pleins phares.",
        "6. Oublier d’allumer le contact avant d’essayer de démarrer.",
        "7. Coller ou faire des appels de phares pour que la voiture devant se pousse.",
        "8. Oublier où vous avez garé votre voiture dans un grand parking.",
        "9. Être distrait et devoir freiner brusquement pour éviter un véhicule.",
        "10. Vouloir allumer les essuie-glaces et allumer les phares par erreur.",
        "11. Tourner à gauche devant un véhicule que vous n’aviez pas vu ou dont vous avez mal jugé la vitesse.",
        "12. Mal évaluer la distance dans un parking et heurter un autre véhicule.",
        "13. Réaliser soudainement que vous ne vous souvenez pas de la portion de route parcourue.",
        "14. Manquer une sortie d’autoroute et devoir faire un détour.",
        "15. Oublier dans quel rapport vous êtes et devoir vérifier.",
        "16. Tenter un dépassement risqué par frustration derrière un véhicule lent.",
        "17. Vous rendre compte que vous suivez un itinéraire habituel au lieu de la destination prévue.",
        "18. Passer à un feu rouge.",
        "19. Poursuivre un conducteur pour « lui dire votre façon de penser ».",
        "20. Oublier de vérifier vos rétroviseurs avant de dépasser et vous faire klaxonner.",
        "21. Ignorer les limites de vitesse tôt le matin ou tard le soir.",
        "22. Oublier la date d’expiration de votre assurance et conduire illégalement.",
        "23. Oublier que vos pleins phares sont allumés jusqu’à être rappelé par un autre conducteur.",
        "24. Tourner à gauche et presque heurter un cycliste à votre droite.",
        "25. Être trop concentré sur la circulation venant de la droite et presque heurter la voiture devant.",
        "26. Conduire après avoir bu plus que la limite autorisée.",
        "27. Manifester votre hostilité envers certains types d’usagers de la route.",
        "28. Regarder la carte ou manipuler la radio au lieu de regarder la route."
    ]
    for i, q in enumerate(dbq_items, 1):
        dbq[i] = st.radio(q, [1, 2, 3, 4, 5, 6], horizontal=True)

    submitted = st.form_submit_button("✅ Soumettre mes réponses")

# ---------- TRAITEMENT ----------
if submitted:
    das_total = sum(das.values())
    violations, errors, lapses = compute_dbq_scores(dbq)

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO responses (
                gender, age_group, education, driving_experience, weekly_time,
                reminder_method, reminder_content,
                das_scores, das_total,
                dbq_scores, violations, errors, lapses
            ) VALUES (
                :gender, :age_group, :education, :driving_experience, :weekly_time,
                :reminder_method, :reminder_content,
                :das_scores, :das_total,
                :dbq_scores, :violations, :errors, :lapses
            )
        """), {
            "gender": gender,
            "age_group": age_group,
            "education": education,
            "driving_experience": driving_experience,
            "weekly_time": weekly_time,
            "reminder_method": reminder_method,
            "reminder_content": reminder_content,
            "das_scores": str(das),
            "das_total": das_total,
            "dbq_scores": str(dbq),
            "violations": violations,
            "errors": errors,
            "lapses": lapses
        })
        conn.commit()

    st.success("✅ Réponses enregistrées avec succès !")

    st.write("### Vos Scores")
    st.metric("Score total DAS (Colère)", das_total)
    st.metric("Violations (DBQ)", violations)
    st.metric("Erreurs (DBQ)", errors)
    st.metric("Lapsus (DBQ)", lapses)

# ---------- DASHBOARD ----------
st.markdown("---")
st.header("📊 Tableau de bord des réponses")

if st.button("Actualiser les données"):
    df = pd.read_sql("SELECT * FROM responses", engine)
    st.dataframe(df)
    st.bar_chart(df[["das_total", "violations", "errors", "lapses"]])

# ---------- EXPORT ----------
st.markdown("### 📥 Exporter les données")
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

