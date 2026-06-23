import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# إعداد الصفحة
st.set_page_config(page_title="CQP المسيرة - التحليل البيداغوجي", layout="wide")
st.title("📊 لوحة القيادة البيداغوجية - CQP المسيرة")

# الاعتماد الكلي على الملف المرفق
file_path = "AvancementProgramme2025_ESY0_22_06_2026_12_04_43.xlsx - AvancementProgramme.csv"

@st.cache_data
def load_and_process_data():
    df = pd.read_csv(file_path)
    # تنظيف الأسماء (إزالة الفراغات الزائدة)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_and_process_data()
    
    # 1. إعدادات التصفية
    selected_group = st.sidebar.selectbox("🎯 اختر المجموعة:", sorted(df['Groupe'].unique()))
    group_df = df[df['Groupe'] == selected_group].copy()

    # 2. المؤشرات البيداغوجية
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المجزوءات", len(group_df))
    col2.metric("متوسط نسبة الإنجاز", f"{group_df['Taux Réalisation (P & SYN )'].mean():.1f}%")
    col3.metric("معدل الغياب العام", f"{group_df['Moy Absence'].mean():.1f}%")

    st.markdown("---")

    # 3. الجدول التفاعلي (التحليل البيداغوجي)
    st.subheader(f"📋 تفاصيل الإنجاز - المجموعة: {selected_group}")
    cols_view = ['Code Module', 'Module', 'Formateur Affecté Présentiel Actif', 
                 'MH Totale  DRIF', 'MH Réalisée Globale', 'Taux Réalisation (P & SYN )']
    st.dataframe(group_df[cols_view].sort_values('Taux Réalisation (P & SYN )'), use_container_width=True)

    # 4. الرسوم البيانية (Visual Analytics)
    st.subheader("📈 تقدم المجزوءات حسب المكون")
    fig = px.bar(group_df, x='Code Module', y='Taux Réalisation (P & SYN )', 
                 color='Formateur Affecté Présentiel Actif',
                 title="مستوى التقدم (بالنسبة المئوية)",
                 color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)

    # 5. التنبيهات (الإدارة بالاستثناء)
    st.subheader("🚨 المراقبة الاستباقية (التأخر)")
    laggards = group_df[group_df['Taux Réalisation (P & SYN )'] < 30]
    if not laggards.empty:
        st.error("المجزوءات التي لم تحقق تقدماً كافياً:")
        st.table(laggards[['Code Module', 'Module', 'Formateur Affecté Présentiel Actif']])
    
    # 6. تصدير PDF
    if st.button("📥 تحميل التقرير (PDF)"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=f"Rapport Pedagogique - Groupe {selected_group}", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        for _, row in group_df.iterrows():
            pdf.cell(200, 7, txt=f"{row['Code Module']} | {row['Module']} : {row['Taux Réalisation (P & SYN )']}%", ln=True)
        st.download_button("تحميل الملف", data=pdf.output(dest='S').encode('latin-1'), file_name=f"Rapport_{selected_group}.pdf")

except Exception as e:
    st.error(f"خطأ في قراءة الملف: {e}")
    st.info("تأكد من وجود ملف `AvancementProgramme...csv` في نفس المجلد.")
