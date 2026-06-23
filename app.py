import streamlit as st
import pandas as pd

st.set_page_config(page_title="CQP المسيرة - لوحة القيادة", layout="wide")

st.title("🎛️ نظام القيادة البيداغوجي المطور")

uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف AvancementProgramme.csv", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()

        # --- الحل الجذري هنا: تحويل البيانات إلى أرقام ---
        col_name = 'Taux Réalisation (P & SYN )'
        
        # تحويل النص إلى أرقام، وأي قيمة غير رقمية تصبح NaN
        df[col_name] = pd.to_numeric(df[col_name].astype(str).str.replace('%', ''), errors='coerce')
        # استبدال القيم الفارغة (NaN) بـ 0
        df[col_name] = df[col_name].fillna(0)
        # ---------------------------------------------

        selected_group = st.sidebar.selectbox("🎯 اختر المجموعة:", sorted(df['Groupe'].unique()))
        group_df = df[df['Groupe'] == selected_group]

        st.subheader(f"📊 مؤشرات المجموعة: {selected_group}")
        st.dataframe(group_df, use_container_width=True)
        
        # الآن ستعمل المقارنة بدون أخطاء
        st.subheader("⚠️ تنبيهات التأخر")
        laggards = group_df[group_df[col_name] < 20]
        st.table(laggards[['Code Module', 'Module', col_name]])

    except Exception as e:
        st.error(f"خطأ تقني: {str(e)}")
else:
    st.info("💡 يرجى رفع الملف لبدء التحليل.")
