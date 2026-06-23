import streamlit as st
import pandas as pd

st.set_page_config(page_title="CQP المسيرة - النظام البيداغوجي", layout="wide")
st.title("📊 نظام القيادة البيداغوجي المطور")

uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف AvancementProgramme.csv", type=["csv"])

if uploaded_file is not None:
    # 1. قراءة وتنظيف أولي
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # 2. القائمة التقنية لفرض تحويل البيانات إلى أرقام
    numeric_cols = ['MH Totale  DRIF', 'MH Réalisée Globale', 'Taux Réalisation (P & SYN )']
    
    for col in numeric_cols:
        # تحويل النص لـ (numeric)، أي خلية بها نص أو خطأ تتحول لـ NaN
        df[col] = pd.to_numeric(df[col].astype(str).str.replace('%', '').str.replace(',', ''), errors='coerce')
        # ملء القيم الفارغة (NaN) بـ 0 لضمان نجاح الحسابات
        df[col] = df[col].fillna(0)

    # الآن العمليات الحسابية ستعمل بدون أخطاء
    st.header("1. التحليل الكمي")
    group_summary = df.groupby('Groupe').agg({
        'MH Totale  DRIF': 'sum',
        'MH Réalisée Globale': 'sum',
        'Taux Réalisation (P & SYN )': 'mean'
    }).rename(columns={'Taux Réalisation (P & SYN )': 'Avancement Moyen (%)'})
    
    st.dataframe(group_summary.style.format("{:.1f}"))
    
    st.success("✅ تم تحليل البيانات بنجاح!")
else:
    st.info("💡 يرجى رفع ملف الـ CSV للبدء.")
