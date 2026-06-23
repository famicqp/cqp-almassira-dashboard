import streamlit as st
import pandas as pd

st.set_page_config(page_title="CQP المسيرة - لوحة القيادة", layout="wide")

st.title("🎛️ نظام القيادة البيداغوجي المطور")

# 1. زر رفع الملف بخصائص تنظيف قوية
uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف AvancementProgramme.csv", type=["csv"])

if uploaded_file is not None:
    try:
        # قراءة الملف مع تجاهل السطور الفارغة وتنظيف الأسماء
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        # إزالة الفراغات من الأسماء لضمان المطابقة
        df.columns = df.columns.str.strip()
        
        # التأكد من وجود الأعمدة الضرورية
        required_columns = ['Groupe', 'Module', 'Taux Réalisation (P & SYN )']
        if not all(col in df.columns for col in required_columns):
            st.error(f"⚠️ خطأ في هيكل الملف. تأكد من وجود الأعمدة: {required_columns}")
        else:
            # 2. عرض البيانات وتصفيتها
            st.sidebar.success("تم تحميل الملف بنجاح!")
            selected_group = st.sidebar.selectbox("🎯 اختر المجموعة:", sorted(df['Groupe'].unique()))
            group_df = df[df['Groupe'] == selected_group]
            
            st.subheader(f"📊 مؤشرات المجموعة: {selected_group}")
            st.dataframe(group_df, use_container_width=True)
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {str(e)}")
else:
    st.info("💡 يرجى رفع ملف الـ CSV للبدء.")
