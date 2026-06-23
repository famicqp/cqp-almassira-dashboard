import streamlit as st
import pandas as pd

# 1. واجهة رفع الملف (بدلاً من القراءة التلقائية)
uploaded_file = st.file_uploader("📥 يرجى رفع ملف AvancementProgramme.csv", type=["csv"])

if uploaded_file is not None:
    # قراءة الملف الذي رفعتَه أنت الآن
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # ... باقي كود التحليل الخاص بك ...
    st.success("تم تحميل البيانات بنجاح!")
else:
    st.info("💡 بانتظار رفع الملف للبدء في تحليل البيانات.")
    st.stop() # إيقاف الكود حتى يتم رفع الملف
