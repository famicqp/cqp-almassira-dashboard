import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CQP المسيرة - Dashboard", layout="wide")
st.title("🎛️ لوحة القيادة البيداغوجية - CQP المسيرة")

uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف E-note (CSV)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()
        
        # التأكد من تنظيف عمود المجموعات قبل الفلترة
        if 'Groupe' in df.columns:
            # تحويل القيم لـ string وإزالة الفراغات وحذف القيم الفارغة
            df['Groupe'] = df['Groupe'].astype(str).str.strip()
            df = df[df['Groupe'] != 'nan'] 
            
            # --- الآن الفلترة ستعمل بذكاء ---
            groups = sorted(df['Groupe'].unique().tolist())
            selected_group = st.sidebar.selectbox("🎯 اختر المجموعة:", groups)
            group_df = df[df['Groupe'] == selected_group].copy()
            
            # تحويل الساعات لأرقام (لضمان عمل الـ Dashboard)
            for col in ['MH Totale  DRIF', 'MH Réalisée Globale']:
                if col in group_df.columns:
                    group_df[col] = pd.to_numeric(group_df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

            # 1. بطاقات المؤشرات (KPIs)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("مخطط", f"{group_df['MH Totale  DRIF'].sum():.0f}")
            c2.metric("منجز", f"{group_df['MH Réalisée Globale'].sum():.0f}")
            c3.metric("معدل التقدم", f"{group_df['Taux Réalisation (P & SYN )'].mean():.1f}%")
            c4.metric("عدد المجزوءات", len(group_df))

            # 2. المبيان البصري
            st.subheader("📈 مؤشرات الأداء حسب المجزوءة")
            fig = px.bar(group_df, x='Module', y=['MH Totale  DRIF', 'MH Réalisée Globale'], barmode='group')
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("خطأ: الملف المرفوع لا يحتوي على عمود باسم 'Groupe'.")
            
    except Exception as e:
        st.error(f"خطأ تقني: {e}")
else:
    st.info("💡 يرجى رفع ملف الـ CSV للبدء.")
