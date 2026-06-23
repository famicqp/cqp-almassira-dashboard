import streamlit as st
import pandas as pd
import plotly.express as px

# إعداد الصفحة
st.set_page_config(page_title="CQP المسيرة - لوحة القيادة", layout="wide")
st.title("🎛️ نظام القيادة البيداغوجي المطور")

# 1. تعريف المتغير في البداية لضمان عدم حدوث NameError
uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف AvancementProgramme.csv", type=["csv"])

# 2. التحقق من رفع الملف قبل أي عملية أخرى
if uploaded_file is not None:
    try:
        # قراءة البيانات
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()
        
        # تنظيف البيانات (تحويل للأرقام)
        numeric_cols = ['MH Totale  DRIF', 'MH Réalisée Globale', 'Taux Réalisation (P & SYN )']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('%', '').str.replace(',', ''), errors='coerce').fillna(0)
        
        # تحليل بيداغوجي
        st.sidebar.success("تم تحميل البيانات!")
        selected_group = st.sidebar.selectbox("🎯 اختر المجموعة:", sorted(df['Groupe'].unique()))
        group_df = df[df['Groupe'] == selected_group]
        
        # عرض المؤشرات
        st.subheader(f"📊 مؤشرات المجموعة: {selected_group}")
        st.dataframe(group_df, use_container_width=True)
        
        # التصور البصري
        fig = px.bar(group_df, x='Code Module', y='Taux Réalisation (P & SYN )', title="نسبة الإنجاز حسب المجزوءة")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"خطأ في معالجة البيانات: {e}")
else:
    st.info("💡 يرجى رفع ملف الـ CSV من القائمة الجانبية للبدء.")
