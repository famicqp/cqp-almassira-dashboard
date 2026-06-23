import streamlit as st
import pandas as pd
import plotly.express as px

# 1. إعدادات الصفحة العامة (رؤية المدير)
st.set_page_config(page_title="CQP Al Massira - Dashboard", layout="wide")

# ترويسة المؤسسة الفاخرة
st.markdown("""
    <div style="background-color: #1a5276; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 25px;">
        <h1 style="color: white; margin: 0; font-family: 'Arial';">لوحة القيادة التفاعلية لتسيير المؤسسة والتكوين</h1>
        <p style="color: #ecf0f1; margin: 5px 0 0 0;">مركز التأهيل المهني (CQP) المسيرة — الدار البيضاء</p>
    </div>
""", unsafe_allow_html=True)

# 2. قاعدة بيانات افتراضية بيداغوجية (تتغير ديناميكياً من واجهة الإدخال)
if 'df_stagiaires' not in st.session_state:
    st.session_state.df_stagiaires = pd.DataFrame([
        {"الشعبة": "Electricité de Bâtiment", "المجموعة": "EB101", "المتدرب": "أمين العلمي", "نسبة الغياب": 2.5, "معدل المرور": 14.5, "الوضعية": "مستمر"},
        {"الشعبة": "Electricité d'Entretien Ind.", "المجموعة": "EEI101", "المتدرب": "ياسين شكري", "نسبة الغياب": 14.0, "معدل المرور": 9.5, "الوضعية": "مستمر"},
        {"الشعبة": "Menuiserie Aluminium", "المجموعة": "MA101", "المتدرب": "سارة مرابط", "نسبة الغياب": 0.0, "معدل المرور": 16.2, "الوضعية": "في فترة تدريب (Stage)"},
        {"الشعبة": "Menuiserie", "المجموعة": "M101", "المتدرب": "عمر حدادي", "نسبة الغياب": 6.8, "معدل المرور": 11.0, "الوضعية": "مستمر"}
    ])

if 'df_formateurs' not in st.session_state:
    st.session_state.df_formateurs = pd.DataFrame([
        {"المكون": "AZIZ RACHID", "الشعبة المستهدفة": "Génie Électrique", "الساعات المنجزة": 920, "ساعات DRIF": 1555, "الحالة": "مستقر"},
        {"المكون": "JAMAL QUARIB", "الشعبة المستهدفة": "Génie Électrique", "الساعات المنجزة": 540, "ساعات DRIF": 900, "الحالة": "تأخر في مجزوءة الإلكترونيات"}
    ])

# ----------------- شريط التنقل الجانبي (Sidebar) -----------------
st.sidebar.image("https://img.icons8.com/fluency/96/dashboard.png", width=80)
st.sidebar.title("🎛️ غرف التحكم والمراقبة")
menu = st.sidebar.radio("اختر الواجهة الحالية:", [
    "📊 لوحة المراقبة ومؤشرات الأداء (KPIs)", 
    "✍️ إدخال وتعديل بيانات المتدربين", 
    "👨‍🏫 تسيير الأساتذة والغلاف الزمني"
])

# ----------------- الواجهة الأولى: لوحة المراقبة ومؤشرات الأداء -----------------
if menu == "📊 لوحة المراقبة ومؤشرات الأداء (KPIs)":
    st.subheader("📋 الوضعية العامة للمؤسسة في لمحة")
    
    # بطاقات الأداء الاستراتيجية العليا (KPI Cards)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="👥 إجمالي المتدربين", value=len(st.session_state.df_stagiaires))
    with col2:
        st.metric(label="📉 متوسط الغياب العام", value=f"{st.session_state.df_stagiaires['نسبة الغياب'].mean():.1f}%")
    with col3:
        st.metric(label="🎯 نسبة نجاح المحاكاة", value="92.4%")
    with col4:
        st.metric(label="⏱️ الغلاف المنجز (DRIF)", value=f"{st.session_state.df_formateurs['الساعات المنجزة'].sum()} h")

    st.markdown("---")
    
    # 🥊 مؤشرات القوة والضعف البيداغوجية التلقائية (Strengths & Weaknesses)
    st.subheader("🔍 التحليل البيداغوجي الذكي للمدير")
    col_str, col_weak = st.columns(2)
    
    with col_str:
        st.markdown("""
        <div style="background-color: #d4efdf; padding: 15px; border-radius: 5px; border-right: 5px solid #27ae60;">
            <h4 style="color: #1e8449; margin: 0;">💪 نقـاط القـوة الحالية (Points Forts)</h4>
            <ul style="color: #196f3d; font-size: 11pt; padding-right: 20px;">
                <li><b>التزام كامل بالشعب:</b> نسبة الإنجاز لشعبة Menuiserie Aluminium بلغت 100.25%.</li>
                <li><b>التميز الدراسي:</b> المتدربة سارة مرابط تحقق أعلى معدل مرور (16.2).</li>
                <li><b>النمط التكويني:</b> استقرار تام في التكوين الحضوري لجميع المجموعات.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_weak:
        # استخراج مؤشر ضعف ديناميكي من البيانات (المتدربين الذين يتجاوز غيابهم 10%)
        absent_alerts = st.session_state.df_stagiaires[st.session_state.df_stagiaires['نسبة الغياب'] > 10]['المتدرب'].tolist()
        alerts_text = "، ".join(absent_alerts) if absent_alerts else "لا توجد غيابات خطيرة حالياً"
        
        st.markdown(f"""
        <div style="background-color: #fadbd8; padding: 15px; border-radius: 5px; border-right: 5px solid #cb6155;">
            <h4 style="color: #922b21; margin: 0;">🚨 نقـاط الضعـف والتنبيهات المستعجلة (Points Faibles)</h4>
            <ul style="color: #78281f; font-size: 11pt; padding-right: 20px;">
                <li><b>إنذار غياب حرج:</b> المتدرب ({alerts_text}) تجاوز السطح المسموح به بـ 14% غياب.</li>
                <li><b>تأخر بيداغوجي:</b> المكون JAMAL QUARIB يسجل فجوة بيداغوجية في مادة الإلكترونيات الأساسية.</li>
                <li><b>معدلات العتبة:</b> مجموعة EEI101 تسجل متوسط عام يلامس عتبة الخطر (9.5).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📈 الرسوم البيانية التفاعلية")
    
    # رسم بياني ديناميكي لمعدلات المرور حسب المتدربين والشعب
    fig = px.bar(st.session_state.df_stagiaires, x="المتدرب", y="معدل المرور", color="الشعبة", 
                 title="مقارنة معدلات المرور بين المتدربين وحسب التخصص التقني", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# ----------------- الواجهة الثانية: إدخال وتعديل بيانات المتدربين -----------------
elif menu == "✍️ إدخال وتعديل بيانات المتدربين":
    st.subheader("📝 وحدة إدخال وتحديث بيانات المتدربين")
    
    # 1. نموذج إضافة متدرب جديد
    with st.expander("➕ إضافة متدرب جديد إلى قاعدة البيانات"):
        with st.form("add_stagiaire_form", clear_on_submit=True):
            filiere = st.selectbox("الشعبة التقنية", ["Electricité de Bâtiment", "Electricité d'Entretien Ind.", "Menuiserie Aluminium", "Menuiserie"])
            groupe = st.text_input("رمز المجموعة (مثال: EB101)")
            nom = st.text_input("اسم ونسب المتدرب")
            absences = st.number_input("نسبة الغياب الحالية (%)", min_value=0.0, max_value=100.0, step=0.5)
            note = st.number_input("معدل المرور الحالي (MOYENNE PASSAGE)", min_value=0.0, max_value=20.0, step=0.1)
            statut = st.radio("الوضعية الحالية للمتدرب", ["مستمر", "في فترة تدريب (Stage)", "منقطع"])
            
            submit_btn = st.form_submit_button("💾 حفظ البيانات وتحديث اللوحة فوراً")
            if submit_btn and nom:
                new_row = {"الشعبة": filiere, "المجموعة": groupe, "المتدرب": nom, "نسبة الغياب": absences, "معدل المرور": note, "الوضعية": statut}
                st.session_state.df_stagiaires = pd.concat([st.session_state.df_stagiaires, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"✔️ تم بنجاح تسجيل المتدرب(ة) {nom} في المنظومة الرقمية!")

    # 2. جدول البيانات التفاعلي للتعديل والحذف المباشر
    st.markdown("### 📋 جدول المتدربين الحالي (تعديل مباشر متاح)")
    st.caption("نصيحة للمدير: يمكنك الضغط مرتين على أي خانة في الجدول أدناه لتعديل الاسم، النسبة أو المعدل مباشرة، وستتغير المؤشرات التلقائية بالتبعية!")
    
    # تفعيل خاصية التعديل التفاعلي داخل الجدول
    edited_df = st.data_editor(st.session_state.df_stagiaires, num_rows="dynamic", use_container_width=True)
    st.session_state.df_stagiaires = edited_df

# ----------------- الواجهة الثالثة: تسيير الأساتذة والغلاف الزمني -----------------
elif menu == "👨‍🏫 تسيير الأساتذة والغلاف الزمني":
    st.subheader("⏳ جدول تتبع الأغلفة الزمنية الرسمية (DRIF)")
    
    st.dataframe(st.session_state.df_formateurs, use_container_width=True)
    
    st.markdown("### ⚙️ إجراءات هندسية سريعة لمدير المركز:")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 محاكاة تصفير عدادات الإسناد السنوي (Reset to Zero)"):
            st.warning("تم تصفير الحصص المنجزة لتسهيل إعادة التوزيع والتحضير لجدولة فترات التدريب الميداني (Stages) للموسم المقبل.")
    with col_btn2:
        st.button("📥 تصدير وثيقة الحصيلة الرسمية كمذكرة PDF للجهة")
