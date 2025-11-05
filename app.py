import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ---------- Configuration ----------
st.set_page_config(page_title="Évaluation : Colère et Perceptions de Conduite", layout="centered")
DB_PATH = "sqlite:///data.db"
engine = create_engine(DB_PATH)

# ---------- Initialisation ----------
st.title("🧠 Questionnaire : Colère, Comportements et Perceptions de Conduite")

# Crée la table si elle n’existe pas
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gender TEXT,
            age_group TEXT,
            education TEXT,
            driving_experience TEXT,
            driving_time TEXT,
            reminder_method TEXT,
            reminder_content TEXT,
            das_scores TEXT,
            das_total INTEGER,
            distracted_total INTEGER,
            anxious_total INTEGER,
            conservative_total INTEGER,
            adventurous_total INTEGER,
            angry_total INTEGER,
            usefulness_total INTEGER,
            risk_total INTEGER,
            trust_total INTEGER,
            usage_total INTEGER,
            intention_total INTEGER
        )
    """))
    conn.commit()

# ---------- FORMULAIRE ----------
with st.form("questionnaire"):
    st.subheader("👤 Partie 0 : Informations générales")

    gender = st.selectbox("Genre :", ["Femme", "Homme"])
    age_group = st.selectbox("Âge :", ["18–23", "24–34", "35–45", "46–60", "Plus de 60"])
    education = st.selectbox("Niveau d’éducation :", [
        "Collège ou moins",
        "Lycée / École professionnelle",
        "Université (bac +2 / DUT / BTS)",
        "Licence / Baccalauréat universitaire",
        "Master ou plus"
    ])
    driving_experience = st.selectbox("Expérience de conduite :", [
        "Moins d’un an",
        "1–5 ans",
        "5–10 ans",
        "10–20 ans",
        "Plus de 20 ans"
    ])
    driving_time = st.selectbox("Temps moyen de conduite hebdomadaire :", [
        "Moins de 5 heures",
        "5–20 heures",
        "20–40 heures",
        "40–60 heures",
        "Plus de 60 heures"
    ])
    reminder_method = st.selectbox("Méthode de rappel préférée :", [
        "Forme auditive (ex. : annonce vocale)",
        "Forme visuelle (ex. : texte à l’écran)",
        "Forme tactile (ex. : vibration du volant)",
        "Rappel combiné (multi-méthodes)",
        "Autre"
    ])
    reminder_content = st.selectbox("Contenu du rappel préféré :", [
        "Rappel du nombre de secondes restantes",
        "Rappel de l’état du feu (rouge / vert / orange)",
        "Rappel de la vitesse recommandée",
        "Autre"
    ])

    # ---------- ÉCHELLES PRINCIPALES ----------
    st.markdown("---")
    st.subheader("🚗 Partie 1 : Comportements et Perceptions de Conduite")
    st.text("Échelle de Likert : 1 = Pas du tout d’accord, 5 = Tout à fait d’accord")

    def likert_block(title, items):
        st.markdown(f"**{title}**")
        responses = {}
        for code, question in items.items():
            responses[code] = st.radio(question, [1, 2, 3, 4, 5], horizontal=True, key=code)
        return responses

    # Distracted
    distracted = likert_block("Distracted", {
        "FX1": "I once misjudged the distance between vehicles due to being distracted while driving, and had to immediately slow down.",
        "FX2": "When driving, I communicate and chat with the passengers.",
        "FX3": "When driving, I will 'pass the time' by playing with my phone, listening to the radio, or enjoying the scenery outside."
    })

    # Anxious
    anxious = likert_block("Anxious", {
        "JL1": "I feel nervous when driving.",
        "JL2": "When driving, I always worry about hitting pedestrians or vehicles.",
        "JL3": "On uncongested highways, I usually drive at or slightly below the speed limit."
    })

    # Conservative
    conservative = likert_block("Conservative", {
        "BS1": "My driving behavior follows the motto 'better safe than sorry'.",
        "BS2": "I understand the driving behaviors of others and stay ready for unexpected maneuvers.",
        "BS3": "I prefer to keep a safe distance and rarely overtake."
    })

    # Adventurous
    adventurous = likert_block("Adventurous", {
        "MX1": "I will deliberately keep close to the vehicle ahead to prevent others from cutting in.",
        "MX2": "When the green light turns yellow, I will drive straight through.",
        "MX3": "When there’s traffic congestion, I will choose faster alternate routes."
    })

    # Angry
    angry = likert_block("Angry", {
        "FN1": "When dissatisfied, I flash lights or honk at other vehicles.",
        "FN2": "I often feel displeased with the behavior of some drivers.",
        "FN3": "During rush hour, I often feel anxious and impatient."
    })

    # Perceived usefulness
    usefulness = likert_block("Perceived Usefulness", {
        "GZYYX1": "I believe that the ‘traffic light’ countdown can enhance my driving experience.",
        "GZYYX2": "The countdown can help me adjust my driving speed promptly.",
        "GZYYX3": "The countdown can reduce my anxiety in traffic jams.",
        "GZYYX4": "The countdown helps me avoid blind spots and save travel time."
    })

    # Perceived risk
    risk = likert_block("Perceived Risk", {
        "GZFXX1": "I'm concerned that the countdown data may be inaccurate.",
        "GZFXX2": "I'm concerned about legal liability if an accident happens because of the countdown.",
        "GZFXX3": "Focusing on the countdown could distract my attention.",
        "GZFXX4": "The green light countdown may prompt some drivers to rush through intersections."
    })

    # Trust
    trust = likert_block("Trust", {
        "XR1": "I believe the countdown function is reliable.",
        "XR2": "Overall, I am willing to use the countdown function.",
        "XR3": "I would recommend the countdown feature to others."
    })

    # Usage conditions
    usage = likert_block("Usage Conditions", {
        "SYTJ1": "I prefer to use it once implemented at all intersections.",
        "SYTJ2": "I think the countdown is very convenient to use.",
        "SYTJ3": "I prefer using it when I'm stuck in traffic or unfamiliar with the road.",
        "SYTJ4": "Regarding the reminder method, I prefer…",
        "SYTJ5": "Regarding the reminder content, I prefer…"
    })

    # Behavioral intention
    intention = likert_block("Behavioral Intention", {
        "XWYX1": "What is your opinion on the ‘traffic light’ countdown function in navigation?",
        "XWYX2": "Do you think the countdown is useful to society?",
        "XWYX3": "How receptive are you to the countdown in navigation?",
        "XWYX4": "What impact do you think the countdown will have on existing traffic?"
    })

    submitted = st.form_submit_button("✅ Soumettre mes réponses")

# ---------- TRAITEMENT ----------
if submitted:
    def avg(values): return sum(values.values()) / len(values)

    # Calcul des scores moyens
    distracted_total = avg(distracted)
    anxious_total = avg(anxious)
    conservative_total = avg(conservative)
    adventurous_total = avg(adventurous)
    angry_total = avg(angry)
    usefulness_total = avg(usefulness)
    risk_total = avg(risk)
    trust_total = avg(trust)
    usage_total = avg(usage)
    intention_total = avg(intention)

    das_total = sum([
        distracted_total, anxious_total, conservative_total,
        adventurous_total, angry_total
    ])  # score global "émotion/conduite"

    # Sauvegarde
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO responses (
                gender, age_group, education, driving_experience, driving_time,
                reminder_method, reminder_content,
                das_scores, das_total,
                distracted_total, anxious_total, conservative_total, adventurous_total, angry_total,
                usefulness_total, risk_total, trust_total, usage_total, intention_total
            )
            VALUES (
                :gender, :age_group, :education, :driving_experience, :driving_time,
                :reminder_method, :reminder_content,
                :das_scores, :das_total,
                :distracted_total, :anxious_total, :conservative_total, :adventurous_total, :angry_total,
                :usefulness_total, :risk_total, :trust_total, :usage_total, :intention_total
            )
        """), {
            "gender": gender,
            "age_group": age_group,
            "education": education,
            "driving_experience": driving_experience,
            "driving_time": driving_time,
            "reminder_method": reminder_method,
            "reminder_content": reminder_content,
            "das_scores": str({
                **distracted, **anxious, **conservative,
                **adventurous, **angry, **usefulness,
                **risk, **trust, **usage, **intention
            }),
            "das_total": das_total,
            "distracted_total": distracted_total,
            "anxious_total": anxious_total,
            "conservative_total": conservative_total,
            "adventurous_total": adventurous_total,
            "angry_total": angry_total,
            "usefulness_total": usefulness_total,
            "risk_total": risk_total,
            "trust_total": trust_total,
            "usage_total": usage_total,
            "intention_total": intention_total
        })
        conn.commit()

    st.success("✅ Réponses enregistrées avec succès !")

    st.write("### Vos Scores Moyens par Dimension")
    st.metric("Distracted", round(distracted_total, 2))
    st.metric("Anxious", round(anxious_total, 2))
    st.metric("Conservative", round(conservative_total, 2))
    st.metric("Adventurous", round(adventurous_total, 2))
    st.metric("Angry", round(angry_total, 2))
    st.metric("Usefulness", round(usefulness_total, 2))
    st.metric("Risk", round(risk_total, 2))
    st.metric("Trust", round(trust_total, 2))
    st.metric("Usage", round(usage_total, 2))
    st.metric("Intention", round(intention_total, 2))

# ---------- DASHBOARD ----------
st.markdown("---")
st.header("📊 Tableau de bord (résultats cumulés)")

if st.button("Actualiser les données"):
    df = pd.read_sql("SELECT * FROM responses", engine)
    st.dataframe(df)
    st.bar_chart(df[[
        "distracted_total", "anxious_total", "conservative_total",
        "adventurous_total", "angry_total",
        "usefulness_total", "risk_total", "trust_total", "usage_total", "intention_total"
    ]])

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
