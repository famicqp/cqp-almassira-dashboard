import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="CQP المسيرة - لوحة القيادة الرقمية", layout="wide")

st.markdown("""<style>.stMetric {background-color: #f0f2f6; padding: 10px; border-radius: 10px;}</style>""", unsafe_allow_html=True)

st.title("🎛️ لوحة القيادة البيداغوجية - CQP المسيرة")

# 2. رفع الملف
uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف AvancementProgramme.csv", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 3. تصفية البيانات
    group = st.sidebar.selectbox("🎯 اختر المجموعة:", sorted(df['Groupe'].unique()))
    group_df = df[df['Groupe'] == group].copy()
    
    # 4. المؤشرات (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("المجزوءات الإجمالية", len(group_df))
    col2.metric("نسبة الإنجاز المتوسطة", f"{group_df['Taux Réalisation (P & SYN )'].mean():.1f}%")
    col3.metric("معدل الغياب العام", f"{group_df['Moy Absence'].mean():.1f}%")

    st.markdown("---")

    # 5. الجدول التفاعلي
    st.subheader(f"📋 تفاصيل التتبع البيداغوجي - مجموعة {group}")
    cols_view = ['Code Module', 'Module', 'Formateur Affecté Présentiel Actif', 'MH Totale  DRIF', 'MH Réalisée Globale', 'Taux Réalisation (P & SYN )']
    st.dataframe(group_df[cols_view].sort_values('Taux Réalisation (P & SYN )'), use_container_width=True)

    # 6. التحليل البصري
    fig = px.bar(group_df, x='Code Module', y='Taux Réalisation (P & SYN )', color='Formateur Affecté Présentiel Actif', 
                 title="مستوى تقدم المجزوءات (الأخضر = إنجاز عالٍ)", color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)

    # 7. التنبيهات (المجزوءات المتأخرة)
    st.subheader("🚨 تنبيهات الإدارة (المجزوءات التي لم تبدأ/متأخرة)")
    laggards = group_df[group_df['Taux Réalisation (P & SYN )'] < 20]
    if not laggards.empty:
        st.error("المجزوءات التي لم تحقق بعد تقدماً ملموساً:")
        st.table(laggards[['Code Module', 'Module', 'Formateur Affecté Présentiel Actif']])
    else:
        st.success("الوضعية البيداغوجية مستقرة.")

    # 8. تصدير PDF
    def generate_pdf(data, group_name):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=f"Rapport CQP Al Massira - Groupe {group_name}", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=10)
        for _, row in data.iterrows():
            pdf.cell(200, 7, txt=f"{row['Code Module']} | {row['Module']} : {row['Taux Réalisation (P & SYN )']}%", ln=True)
        return pdf.output(dest='S').encode('latin-1')

    if st.button("📥 تحميل تقرير PDF"):
        pdf_bytes = generate_pdf(group_df, group)
        st.download_button("اضغط للتحميل", data=pdf_bytes, file_name=f"Rapport_{group}.pdf", mime="application/pdf")

else:
    st.info("💡 التعليمات: ارفع ملف E-note (CSV) للبدء.")
    
