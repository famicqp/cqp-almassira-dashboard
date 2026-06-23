import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="CQP المسيرة - لوحة المراقبة", layout="wide")

st.title("📊 لوحة القيادة البيداغوجية: نظام المتابعة الآلي")

# قراءة الملف الذي أرفقته
# ملاحظة: تأكد من وجود ملف AvancementProgramme.csv في نفس المجلد
try:
    df = pd.read_csv("AvancementProgramme2025_ESY0_22_06_2026_12_04_43.xlsx - AvancementProgramme.csv")
    df.columns = df.columns.str.strip()

    # القائمة الجانبية للتحكم
    st.sidebar.header("إعدادات المراقبة")
    groups = sorted(df['Groupe'].unique())
    selected_group = st.sidebar.selectbox("اختر المجموعة (Groupe):", groups)

    # معالجة بيانات المجموعة المختارة
    group_df = df[df['Groupe'] == selected_group].copy()

    # المؤشرات الرئيسية
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد المجزوءات", len(group_df))
    col2.metric("متوسط الإنجاز العام", f"{group_df['Taux Réalisation (P & SYN )'].mean():.1f}%")
    
    st.markdown("---")

    # الجدول التفصيلي (الذي يحتوي على المكون والمجزوءة)
    st.subheader(f"تفاصيل الإنجاز لمجموعة: {selected_group}")
    cols_to_display = ['Code Module', 'Module', 'Formateur Affecté Présentiel Actif', 
                       'MH Totale  DRIF', 'MH Réalisée Globale', 'Taux Réalisation (P & SYN )']
    st.dataframe(group_df[cols_to_display].sort_values(by='Taux Réalisation (P & SYN )'), use_container_width=True)

    # الرسم البياني (للتحليل البصري)
    fig = px.bar(group_df, x='Code Module', y='Taux Réalisation (P & SYN )', 
                 color='Formateur Affecté Présentiel Actif',
                 title=f"خارطة تقدم المجزوءات لمجموعة {selected_group}")
    st.plotly_chart(fig, use_container_width=True)

    # زر تصدير التقرير
    if st.button("📥 تحميل تقرير PDF للمجموعة"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=f"Rapport de Suivi - Groupe {selected_group}", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        for _, row in group_df.iterrows():
            pdf.cell(200, 7, txt=f"{row['Code Module']} - {row['Module']} : {row['Taux Réalisation (P & SYN )']}%", ln=True)
        st.download_button("تحميل الملف", data=pdf.output(dest='S').encode('latin-1'), file_name="Rapport.pdf")

except FileNotFoundError:
    st.error("⚠️ لم يتم العثور على الملف. تأكد من تسمية ملف الـ CSV بنفس الاسم المذكور في الكود.")
