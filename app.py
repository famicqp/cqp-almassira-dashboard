import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Expert - CQP المسيرة", layout="wide")

st.title("📊 تقرير التحليل البيداغوجي المتقدم - CQP المسيرة")

# 1. فحص وبناء البيانات (Data Audit & Processing)
def process_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    # تنظيف القيم المفقودة في أعمدة الساعات
    time_cols = ['MH Totale  DRIF', 'MH Réalisée Globale']
    for col in time_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # حساب الفارق البيداغوجي (Écart)
    df['Écart'] = df['MH Réalisée Globale'] - df['MH Totale  DRIF']
    return df

uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف AvancementProgramme.csv", type=["csv"])

if uploaded_file:
    df = process_data(uploaded_file)
    
    # 2. التحليل الكمي (Quantitative Analysis)
    st.header("1. التحليل الكمي وتتبع التقدم")
    group_summary = df.groupby('Groupe').agg({
        'MH Totale  DRIF': 'sum',
        'MH Réalisée Globale': 'sum',
        'Taux Réalisation (P & SYN )': 'mean'
    }).reset_index()
    
    st.dataframe(group_summary.style.format({'Taux Réalisation (P & SYN )': '{:.2f}%'}))

    # 3. رصد الفوارق والتنبيهات (Discrepancies & Alerts)
    st.header("2. التنبيهات الذكية (Alerts)")
    laggards = df[df['Taux Réalisation (P & SYN )'] < 50][['Groupe', 'Module', 'Formateur Affecté Présentiel Actif', 'Écart']]
    st.warning("🚨 المجزوءات التي تتطلب تدخلاً (تأخر في الإنجاز):")
    st.table(laggards)

    # 4. التصور البصري (Data Visualization)
    st.header("3. التصور البصري للأداء")
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(df, x='Formateur Affecté Présentiel Actif', y='MH Réalisée Globale', 
                      color='Groupe', title="أداء المكونين (Réalisation par Formateur)")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.pie(group_summary, values='Taux Réalisation (P & SYN )', names='Groupe', 
                      title="نسبة تقدم المجموعات (Progression par Groupe)")
        st.plotly_chart(fig2, use_container_width=True)

    # 5. التقرير الختامي والتوصيات
    st.header("4. التقرير الختامي والتوصيات (Executive Summary)")
    st.markdown("""
    * **الحالة الراهنة:** يتم رصد تفاوت في معدلات الإنجاز بين شعبة النجارة والكهرباء.
    * **خطة العمل المقترحة (Action Plan):**
        1. **إعادة توزيع الساعات:** للمكونين الذين سجلوا (Écart positif) كبير.
        2. **الدعم البيداغوجي:** تخصيص حصص إضافية للمجزوءات التي سجلت (Taux < 50%).
        3. **تحديث البيانات:** مراقبة دقيقة للمجزوءات المسندة ولم تبدأ بعد.
    """)
