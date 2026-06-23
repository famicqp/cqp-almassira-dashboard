import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

st.set_page_config(page_title="CQP المسيرة - لوحة الإدارة الذكية", layout="wide")

st.title("🚀 نظام الإدارة البيداغوجية الاستباقي")

uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف E-note (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تحويل الأعمدة إلى أرقام (التنظيف الجذري)
    for col in ['MH Totale  DRIF', 'MH Réalisée Globale']:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
    # 1. حساب "مؤشر الخطر البيداغوجي"
    df['Remaining_Hours'] = df['MH Totale  DRIF'] - df['MH Réalisée Globale']
    df['Progress_%'] = (df['MH Réalisée Globale'] / df['MH Totale  DRIF'] * 100).fillna(0)
    
    # 2. لوحة القيادة التفاعلية
    selected_group = st.sidebar.selectbox("🎯 اختر المجموعة:", sorted(df['Groupe'].unique()))
    group_df = df[df['Groupe'] == selected_group]
    
    # 3. جدول التحليل الاستباقي (الإدارة بالاستثناء)
    st.subheader(f"⚠️ وضعية المجموعة: {selected_group}")
    
    # تسليط الضوء على المجزوءات التي تحتاج تدخلاً (Remaining > 0 و Progress < 80%)
    st.dataframe(group_df[['Module', 'Formateur Affecté Présentiel Actif', 'Remaining_Hours', 'Progress_%']]
                 .sort_values(by='Remaining_Hours', ascending=False),
                 use_container_width=True)

    # 4. التوصيات البيداغوجية
    st.header("💡 توصيات خبير هندسة التكوين")
    if group_df['Progress_%'].mean() < 50:
        st.error("🚨 إنذار: هذه المجموعة تسير بوتيرة بطيئة جداً. يجب عقد اجتماع مع المكونين فوراً.")
    else:
        st.success("✅ وتيرة التكوين مقبولة.")
        
else:
    st.info("💡 يرجى رفع الملف لبدء التحليل الاستباقي.")
