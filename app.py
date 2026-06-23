import streamlit as st
import pandas as pd

# تحميل البيانات
@st.cache_data
def get_data():
    df = pd.read_csv("AvancementProgramme2025_ESY0_22_06_2026_12_04_43.xlsx - AvancementProgramme.csv")
    df.columns = df.columns.str.strip()
    return df

df = get_data()

st.title("📑 التقارير البيداغوجية الشاملة")

# 1. تقرير الشعب (Filières)
st.subheader("🏢 تقرير الشعب (Filière Report)")
filiere_report = df.groupby('filière').agg({
    'MH Totale  DRIF': 'sum',
    'MH Réalisée Globale': 'sum',
    'Taux Réalisation (P & SYN )': 'mean'
}).rename(columns={'Taux Réalisation (P & SYN )': 'Moyenne Avancement %'})
st.dataframe(filiere_report.style.format("{:.1f}"))

# 2. تقرير المكونين (Formateurs)
st.subheader("👨‍🏫 تقرير الأداء المهني للمكونين")
formateur_report = df.groupby('Formateur Affecté Présentiel Actif').agg({
    'Module': 'count',
    'MH Réalisée Globale': 'sum'
}).rename(columns={'Module': 'Nombre de Modules', 'MH Réalisée Globale': 'Heures Totales'})
st.dataframe(formateur_report.sort_values(by='Heures Totales', ascending=False))

# 3. تقرير المتدربين (حسب المجموعات - Groupes)
st.subheader("🎓 تقرير المجموعات (Groupes/Stagiaires)")
groupe_report = df.groupby('Groupe').agg({
    'Effectif Groupe': 'first',
    'Moy Absence': 'mean',
    'Taux Réalisation (P & SYN )': 'mean'
})
st.dataframe(groupe_report)

st.info("💡 هذه التقارير تلخص الأداء العام للمركز (CQP المسيرة).")
