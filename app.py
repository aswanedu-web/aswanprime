import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("📊 نظام تحليل الكثافات الطلابية - 2026")

uploaded_file = st.file_uploader("قم برفع ملف الإحصاء المعدل", type=["csv"])

if uploaded_file is not None:
    # قائمة بالترميزات المحتملة للملفات العربية
    encodings = ['utf-8', 'windows-1256', 'utf-8-sig', 'cp1256']
    df = None
    
    # محاولة قراءة الملف بتجربة كل ترميز
    for enc in encodings:
        try:
            uploaded_file.seek(0) # إعادة قراءة الملف من البداية
            df = pd.read_csv(uploaded_file, skiprows=3, encoding=enc)
            break 
        except:
            continue

    if df is not None:
        try:
            # تنظيف الأعمدة (بناءً على الملف الأخير):
            # العمود 0: الإدارة، العمود 14: إجمالي الفصول، العمود 15: إجمالي التلاميذ
            df_clean = df.iloc[:, [0, 14, 15]].copy()
            df_clean.columns = ['الإدارة', 'الفصول', 'التلاميذ']
            
            # تحويل البيانات لأرقام وحذف السطور الفارغة
            df_clean = df_clean.dropna(subset=['الإدارة'])
            df_clean['الفصول'] = pd.to_numeric(df_clean['الفصول'], errors='coerce')
            df_clean['التلاميذ'] = pd.to_numeric(df_clean['التلاميذ'], errors='coerce')
            df_clean = df_clean.dropna()

            # حساب متوسط الكثافة
            df_clean['الكثافة'] = df_clean['التلاميذ'] / df_clean['الفصول']
            
            # مؤشر التحذير
            threshold = 40
            
            # --- الرسم البياني ---
            st.subheader("📈 مؤشر الكثافة حسب الإدارة")
            fig, ax = plt.subplots(figsize=(10, 5))
            colors = ['#d32f2f' if x > threshold else '#388e3c' for x in df_clean['الكثافة']]
            
            sns.barplot(x='الإدارة', y='الكثافة', data=df_clean, palette=colors, ax=ax)
            ax.axhline(y=threshold, color='red', linestyle='--', label=f'حد الكثافة ({threshold})')
            ax.set_title("متوسط عدد التلاميذ في الفصل الواحد")
            st.pyplot(fig)

            # --- عرض الجدول الملون ---
            st.subheader("📋 تقرير مؤشرات الإنذار")
            
            def color_alert(val):
                color = 'red' if val > threshold else 'green'
                return f'background-color: {color}; color: white; font-weight: bold'

            st.table(df_clean.style.applymap(color_alert, subset=['الكثافة']))

        except Exception as e:
            st.error(f"خطأ في هيكلة الأعمدة: {e}")
    else:
        st.error("تعذر قراءة الملف، يرجى التأكد من حفظه بصيغة CSV (UTF-8) أو CSV (Windows).")
