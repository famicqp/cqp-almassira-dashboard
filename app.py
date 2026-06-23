import streamlit as st
import pandas as pd

# 1. إعداد النظام
st.set_page_config(page_title="CQP المسيرة - لوحة التقارير", layout="wide")
st.title("📑 نظام التقارير البيداغوجية المتكامل")

# 2. تحميل البيانات (اعتماد كلي على ملفك)
@st.cache_data
def load_data():
    df = pd.read_csv("AvancementProgramme2025_ESY0_22_06_2026_12_04_43.xlsx - AvancementProgramme.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# 3. تبويب التقارير
tab1, tab2, tab3 = st.tabs(["🏢 تقرير الشعب", "👨‍🏫 تقرير المكونين", "🎓 تقرير المجموعات"])

with tab1:
    st.subheader("تحليل الشعب (Filières)")
    filiere_rep = df.groupby('filière').agg({'MH Totale  DRIF': 'sum', 'MH Réalisée Globale': 'sum', 'Taux Réalisation (P & SYN )': 'mean'})
    st.dataframe(filiere_rep.style.format("{:.1f}"))

with tab2:
    st.subheader("أداء المكونين (Formateurs)")
    formateur_rep = df.groupby('Formateur Affecté Présentiel Actif').agg({'Module': 'count', 'MH Réalisée Globale': 'sum'})
    st.dataframe(formateur_rep.sort_values(by='MH Réalisée Globale', ascending=False))

with tab3:
    st.subheader("تقرير المجموعات (Groupes)")
    groupe_rep = df.groupby('Groupe').agg({'Effectif Groupe': 'first', 'Moy Absence': 'mean', 'Taux Réalisation (P & SYN )': 'mean'})
    st.dataframe(groupe_rep.sort_values(by='Taux Réalisation (P & SYN )'))
