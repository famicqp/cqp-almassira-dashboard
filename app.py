import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CQP المسيرة - لوحة القيادة", layout="wide")
st.title("🎛️ نظام القيادة البيداغوجي الرقمي")

# 1. واجهة رفع الملف (الحل الجذري للمشكلة)
uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف AvancementProgramme.csv", type=["csv"])

if uploaded_file is not None:
    # 2. معالجة البيانات
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 3. اختيار المجموعة (الفلترة)
    selected_group = st.sidebar.selectbox("🎯 اختر المجموعة:", sorted(df['Groupe'].unique()))
    group_df = df[df['Groupe'] == selected_group].copy()
    
    # 4. لوحة المؤشرات (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المجزوءات", len(group_df))
    col2.metric("متوسط نسبة التقدم", f"{group_df['Taux Réalisation (P & SYN )'].mean():.1f}%")
    col3.metric("معدل الغياب العام", f"{group_df['Moy Absence'].mean():.1f}%")
    
    # 5. عرض الجداول التحليلية
    st.subheader(f"📋 تفاصيل التتبع البيداغوجي - {selected_group}")
    st.dataframe(group_df[['Code Module', 'Module', 'Formateur Affecté Présentiel Actif', 
                           'MH Totale  DRIF', 'MH Réalisée Globale', 'Taux Réalisation (P & SYN )']], 
                 use_container_width=True)
    
    # 6. التصور البصري (الاعتماد على بيانات الساعات المنجزة)
    fig = px.bar(group_df, x='Code Module', y='Taux Réalisation (P & SYN )', 
                 color='Formateur Affecté Présentiel Actif',
                 title="مخطط تقدم الإنجاز حسب المجزوءة")
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.warning("⚠️ يرجى رفع ملف الـ CSV للبدء.")
    st.markdown("""
    ### تعليمات:
    1. اضغط على زر 'Browse files' في القائمة الجانبية.
    2. اختر ملف `AvancementProgramme...csv` الخاص بك.
    3. سيقوم النظام فوراً باستخراج التقارير المطلوبة.
    """)
