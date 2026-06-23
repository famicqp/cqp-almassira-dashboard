import streamlit as st
import pandas as pd

st.set_page_config(page_title="CQP المسيرة - لوحة الإدارة", layout="wide")
st.title("🚀 نظام الإدارة البيداغوجية الاستباقي")

uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف E-note (CSV)", type=["csv"])

if uploaded_file is not None:
    try:
        # قراءة البيانات
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()
        
        # التأكد من وجود عمود 'Groupe'
        if 'Groupe' not in df.columns:
            st.error("⚠️ الملف المرفوع لا يحتوي على عمود 'Groupe'. يرجى التأكد من اختيار الملف الصحيح.")
        else:
            # تنظيف البيانات
            for col in ['MH Totale  DRIF', 'MH Réalisée Globale']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            
            # حارس (Guard): التأكد من عدم وجود قيم فارغة في عمود المجموعة
            df['Groupe'] = df['Groupe'].fillna("غير محدد")
            
            # الفلترة الآمنة
            groups = sorted(df['Groupe'].dropna().unique())
            selected_group = st.sidebar.selectbox("🎯 اختر المجموعة:", groups)
            
            group_df = df[df['Groupe'] == selected_group]
            
            st.subheader(f"📊 وضعية المجموعة: {selected_group}")
            st.dataframe(group_df, use_container_width=True)
            
    except Exception as e:
        st.error(f"خطأ في معالجة الملف: {e}")
else:
    st.info("💡 يرجى رفع ملف الـ CSV للبدء.")
