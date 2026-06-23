import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CQP المسيرة - لوحة المدير", layout="wide")

st.title("🎛️ لوحة القيادة البيداغوجية (تعديل مباشر)")

# إنشاء جدول افتراضي (يمكنك استبدال البيانات هنا ببياناتك)
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        'Code Module': ['M101', 'M102', 'M103'],
        'Module': ['الكهرباء', 'الميكانيك', 'النجارة'],
        'Taux Réalisation (P & SYN )': [50.0, 75.0, 20.0],
        'Formateur': ['أ. أحمد', 'أ. محمد', 'أ. علي']
    })

# جدول قابل للتعديل (هنا يمكنك تعديل الأرقام مباشرة من هاتفك)
st.subheader("✍️ عدّل البيانات هنا مباشرة:")
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic")

# زر الحفظ (لتثبيت التعديلات في الجلسة)
if st.button("حفظ التغييرات"):
    st.session_state.df = edited_df
    st.success("تم حفظ البيانات بنجاح!")

# تحليل البيانات بعد التعديل
st.subheader("📊 التحليل البصري:")
fig = px.bar(edited_df, x='Code Module', y='Taux Réalisation (P & SYN )', color='Formateur')
st.plotly_chart(fig, use_container_width=True)
