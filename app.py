import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CQP المسيرة - Dashboard", layout="wide")

# تخصيص واجهة اللوحة
st.title("🎛️ لوحة القيادة البيداغوجية - CQP المسيرة")

uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف E-note (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # تحويل الأرقام (تطهير البيانات)
    for col in ['MH Totale  DRIF', 'MH Réalisée Globale']:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
    # اختيار المجموعة
    selected_group = st.sidebar.selectbox("🎯 اختر المجموعة:", sorted(df['Groupe'].unique()))
    group_df = df[df['Groupe'] == selected_group].copy()
    
    # --- 1. بطاقات المؤشرات (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)
    avg_prog = group_df['Taux Réalisation (P & SYN )'].mean()
    total_mh = group_df['MH Totale  DRIF'].sum()
    done_mh = group_df['MH Réalisée Globale'].sum()
    
    col1.metric("إجمالي الساعات المخططة", f"{total_mh:.0f}")
    col2.metric("إجمالي الساعات المنجزة", f"{done_mh:.0f}")
    col3.metric("معدل التقدم العام", f"{avg_prog:.1f}%")
    col4.metric("عدد المجزوءات", len(group_df))

    # --- 2. التحليل البصري (Dashboard Charts) ---
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📈 التوازن البيداغوجي (مقارنة الساعات)")
        fig = px.bar(group_df, x='Module', y=['MH Totale  DRIF', 'MH Réalisée Globale'], 
                     barmode='group', color_discrete_map={'MH Totale  DRIF': '#1f77b4', 'MH Réalisée Globale': '#2ca02c'})
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("⚖️ توزيع الأداء")
        fig2 = px.pie(group_df, values='MH Réalisée Globale', names='Formateur Affecté Présentiel Actif', 
                      title="حصة المكونين في الإنجاز")
        st.plotly_chart(fig2, use_container_width=True)

    # --- 3. التنبيهات الاستراتيجية ---
    st.subheader("🚨 رادار التدخل البيداغوجي")
    alerts = group_df[group_df['MH Réalisée Globale'] < (group_df['MH Totale  DRIF'] * 0.3)]
    if not alerts.empty:
        st.error("المجزوءات التي تحتاج تدخلاً عاجلاً (تقدم < 30%):")
        st.table(alerts[['Module', 'Formateur Affecté Présentiel Actif', 'Taux Réalisation (P & SYN )']])
    else:
        st.success("الوضع تحت السيطرة: لا توجد مجزوءات متأخرة بشكل حرج.")

else:
    st.info("💡 بانتظار رفع ملف E-note لعرض لوحة القيادة.")
