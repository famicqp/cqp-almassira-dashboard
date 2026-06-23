import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# إعداد واجهة النظام
st.set_page_config(page_title="CQP المسيرة - لوحة التحليل الاستراتيجي", layout="wide")
st.title("📊 لوحة القيادة البيداغوجية - CQP المسيرة")

# 1. مرحلة التدقيق وتنظيف البيانات (Data Audit & Cleaning)
def load_and_clean_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    
    # تنظيف أعمدة الساعات وتحويلها لأرقام
    cols_to_fix = ['MH Totale  DRIF', 'MH Réalisée Globale']
    for col in cols_to_fix:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
    # حساب الفارق البيداغوجي (Écart)
    df['Écart'] = df['MH Réalisée Globale'] - df['MH Totale  DRIF']
    return df

uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف AvancementProgramme.csv", type=["csv"])

if uploaded_file:
    df = load_and_clean_data(uploaded_file)
    
    # 2. التحليل الكمي وتتبع التقدم (Quantitative Analysis)
    st.header("1. التحليل الكمي (Quantitative Analysis)")
    group_summary = df.groupby('Groupe').agg({
        'MH Totale  DRIF': 'sum',
        'MH Réalisée Globale': 'sum',
        'Taux Réalisation (P & SYN )': 'mean'
    }).rename(columns={'Taux Réalisation (P & SYN )': 'Avancement Moyen (%)'})
    
    st.dataframe(group_summary.style.format("{:.1f}"))

    # 3. رصد الفوارق والتنبيهات (Discrepancies & Alerts)
    st.header("2. الفوارق والتنبيهات الذكية (Smart Alerts)")
    critical_laggards = df[df['Écart'] < -20] # تنبيه للمجزوءات المتأخرة أكثر من 20 ساعة
    
    if not critical_laggards.empty:
        st.warning("⚠️ تنبيه: مجزوءات متأخرة جداً (Écart Négatif):")
        st.table(critical_laggards[['Groupe', 'Module', 'Formateur Affecté Présentiel Actif', 'Écart']])
    else:
        st.success("✅ جميع المجزوءات تسير وفق الجدول الزمني المخطط.")

    # 4. التصور البصري (Data Visualization)
    st.header("3. لوحة التصور البصري (Dashboard)")
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(df, x='Formateur Affecté Présentiel Actif', y=['MH Totale  DRIF', 'MH Réalisée Globale'],
                      title="مقارنة العبء التدريسي (Affectation vs Réalisation)")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        fig2 = px.pie(group_summary, values='Avancement Moyen (%)', names=group_summary.index,
                      title="نسبة تقدم الشعب والمجموعات")
        st.plotly_chart(fig2, use_container_width=True)

    # 5. التقرير الختامي (Executive Summary)
    st.header("4. الخطة الاستراتيجية المقترحة (Action Plan)")
    st.info("""
    * **ملخص الحالة:** تم تحليل وتيرة الإنجاز لكل شعبة (النجارة/الكهرباء).
    * **توصيات الإدارة:**
        1. **إعادة توزيع (Réallocation):** المكونون الذين تجاوزوا (Écart positif) يمكنهم دعم زملائهم.
        2. **المعالجة البيداغوجية:** تكثيف الحصص للمجزوءات التي سجلت تأخراً (Écart négatif).
        3. **المراقبة المستمرة:** تحديث ملف الـ E-note أسبوعياً لضمان دقة المؤشرات.
    """)
    
    

else:
    st.info("💡 قم برفع الملف للبدء في تحليل أداء مركزك.")
