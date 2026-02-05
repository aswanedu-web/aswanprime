import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("📊 نظام تحليل كثافات أسوان 2026")

uploaded_file = st.file_uploader("قم برفع ملف الإحصاء", type=["csv"])

if uploaded_file is not None:
    # 1. حل مشكلة الترميز (Encoding)
    df = None
    for enc in ['utf-8-sig', 'windows-1256', 'cp1256', 'utf-8']:
        try:
            uploaded_file.seek(0)
            # نقرأ الملف بدون skiprows في البداية لنحدد أماكن البيانات
            df = pd.read_csv(uploaded_file, encoding=enc, header=None)
            break
        except:
            continue

    if df is not None:
        try:
            # 2. البحث الديناميكي عن صف "الإدارة"
            # نبحث عن الصف الذي يحتوي على كلمة "أسوان" أو "إدفو" للبدء منه
            start_row = 0
            for i, row in df.iterrows():
                if 'أسوان' in str(row.values):
                    start_row = i
                    break
            
            # إعادة بناء البيانات من صف البداية
            df_data = df.iloc[start_row:].copy()
            
            # 3. استخراج الأعمدة المطلوبة (الإدارة عادة أول عمود، والفصول والتلاميذ آخر عمودين)
            # حسب ملفك: الإدارة في العمود 0، الفصول في العمود قبل الأخير، التلاميذ في العمود الأخير
            final_df = pd.DataFrame()
            final_df['الإدارة'] = df_data.iloc[:, 0]
            final_df['الفصول'] = pd.to_numeric(df_data.iloc[:, -2], errors='coerce')
            final_df['التلاميذ'] = pd.to_numeric(df_data.iloc[:, -1], errors='coerce')
            
            # تنظيف البيانات
            final_df = final_df.dropna().reset_index(drop=True)
            
            # 4. حساب الكثافة ومؤشر التحذير
            final_df['الكثافة'] = final_df['التلاميذ'] / final_df['الفصول']
            threshold = 40

            # --- العرض ---
            st.success("تم تحليل البيانات بنجاح!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("إجمالي التلاميذ", f"{int(final_df['التلاميذ'].sum()):,}")
            with col2:
                st.metric("أعلى كثافة مسجلة", f"{final_df['الكثافة'].max():.1f}")

            # الرسم البياني
            st.subheader("📈 مخطط كثافة الفصول")
            fig, ax = plt.subplots(figsize=(10, 5))
            colors = ['#e74c3c' if x > threshold else '#2ecc71' for x in final_df['الكثافة']]
            sns
