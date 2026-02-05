import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="تحليل كثافة الفصول 2026", layout="wide")

st.title("📊 نظام تحليل بيانات المديرية ومؤشرات الكثافة")

# 1. خاصية رفع الملف لتجنب خطأ FileNotFoundError
uploaded_file = st.file_uploader("قم برفع ملف الإحصاء (CSV)", type=["csv"])

if uploaded_file is not None:
    try:
        # 2. قراءة البيانات مع معالجة الهيكل (تخطي صف واحد كما في ملفك الأخير)
        df = pd.read_csv(uploaded_file, skiprows=1)
        
        # تنظيف وتسمية الأعمدة (بناءً على المعاينة المرفقة)
        # نختار الأعمدة: الإدارة (0)، إجمالي الفصول (14)، إجمالي التلاميذ (15)
        # ملاحظة: قد تختلف الأرقام قليلاً حسب النسخة، لذا سنستخدم التسمية التالية:
        df_clean = df.iloc[:, [0, 14, 15]].copy()
        df_clean.columns = ['الإدارة', 'إجمالي_الفصول', 'إجمالي_التلاميذ']
        
        # حذف الصفوف الفارغة وتحويل النصوص لأرقام
        df_clean = df_clean.dropna(subset=['الإدارة'])
        df_clean['إجمالي_الفصول'] = pd.to_numeric(df_clean['إجمالي_الفصول'], errors='coerce')
        df_clean['إجمالي_التلاميذ'] = pd.to_numeric(df_clean['إجمالي_التلاميذ'], errors='coerce')
        df_clean = df_clean.dropna()

        # 3. حساب متوسط الكثافة
        df_clean['متوسط_الكثافة'] = df_clean['إجمالي_التلاميذ'] / df_clean['إجمالي_الفصول']

        # 4. مؤشر التحذير (حد الكثافة 40)
        threshold = 40
        
        # عرض الإحصائيات العامة في كروت
        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي التلاميذ", f"{int(df_clean['إجمالي_التلاميذ'].sum()):,}")
        col2.metric("إجمالي الفصول", f"{int(df_clean['إجمالي_الفصول'].sum()):,}")
        col3.metric("متوسط الكثافة العام", f"{df_clean['متوسط_الكثافة'].mean():.1f}")

        # 5. الرسم البياني ومؤشر التحذير
        st.subheader("📈 مقارنة الكثافة بين الإدارات التعليمية")
        
        fig, ax = plt.subplots(figsize=(10, 5))
        # تلوين الأعمدة: أحمر للتنبيه، أخضر للمستقر
        colors = ['#e74c3c' if x > threshold else '#2ecc71' for x in df_clean['متوسط_الكثافة']]
        
        sns.barplot(x='الإدارة', y='متوسط_الكثافة', data=df_clean, palette=colors, ax=ax)
        ax.axhline(y=threshold, color='black', linestyle='--', label=f'حد التحذير ({threshold})')
        ax.set_ylabel("تلميذ / فصل")
        ax.set_title("مؤشر الكثافة لكل إدارة")
        
        st.pyplot(fig)

        # 6. جدول البيانات مع حالة التحذير
        def highlight_density(val):
            color = 'red' if val > threshold else 'green'
            return f'color: {color}; font-weight: bold'

        st.subheader("📋 تفاصيل الإدارات ومؤشر الخطر")
        df_display = df_clean.copy()
        df_display['الحالة'] = df_display['متوسط_الكثافة'].apply(lambda x: '⚠️ تجاوز الحد' if x > threshold else '✅ آمن')
        
        st.dataframe(df_display.style.applymap(highlight_density, subset=['متوسط_الكثافة']))

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {e}")
else:
    st.info("بانتظار رفع ملف 'مدارس المديرية وتلاميذ 2026.xlsx - الاحصاء.csv' للبدء في التحليل.")
