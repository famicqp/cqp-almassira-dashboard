import streamlit as st
import pandas as pd
import plotly.express as px

# 1. إعدادات النظام
st.set_page_config(page_title="Dashboard CQP المسيرة", layout="wide")
st.title("🎛️ نظام القيادة البيداغوجي (تحليل بيانات E-note)")

# 2. تحميل البيانات (اعتماد كلي على الملف المرفق)
@st.cache_data
def load_data():
    df = pd.read_csv("AvancementProgramme2025_ESY0_22_06_2026_12_04_43.xlsx - AvancementProgramme.csv")
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    # 3. تصفية المجموعات
    st.sidebar.header("لوحة التحكم")
    selected_group = st.sidebar.selectbox("اختر المجموعة:", sorted(df['Groupe'].unique()))
    group_data = df[df['Groupe'] == selected_group]

    # 4. المؤشرات (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("المجزوءات المسندة", len(group_data))
    col2.metric("متوسط نسبة التقدم", f"{group_data['Taux Réalisation (P & SYN )'].mean():.1f}%")
    
    # 5. تحليل الفوارق (Discrepancies)
    st.subheader("📋 تقرير الأداء التفصيلي")
    view_cols = ['Code Module', 'Module', 'Formateur Affecté Présentiel Actif', 
                 'MH Totale  DRIF', 'MH Réalisée Globale', 'Taux Réalisation (P & SYN )']
    st.dataframe(group_data[view_cols].sort_values(by='Taux Réalisation (P & SYN )'), use_container_width=True)

    # 6. التحليل البصري (الاعتماد على بيانات الساعات)
    st.subheader("📈 تحليل الإنجاز مقابل البرنامج")
    fig = px.bar(group_data, x='Code Module', y=['MH Totale  DRIF', 'MH Réalisée Globale'], 
                 barmode='group', title="مقارنة الساعات المبرمجة بالمنجزة (بالكود)")
    st.plotly_chart(fig, use_container_width=True)

    # 7. التنبيهات (Alerts)
    st.subheader("⚠️ تنبيهات التأخر (Taux < 20%)")
    alerts = group_data[group_data['Taux Réalisation (P & SYN )'] < 20]
    if not alerts.empty:
        st.error("المجزوءات التي سجلت تقدماً ضعيفاً جداً:")
        st.table(alerts[['Code Module', 'Module', 'Formateur Affecté Présentiel Actif', 'Taux Réalisation (P & SYN )']])
    else:
        st.success("الوضعية البيداغوجية طبيعية.")

except Exception as e:
    st.error("يرجى التأكد من أن ملف البيانات موجود في نفس مجلد التشغيل.")
