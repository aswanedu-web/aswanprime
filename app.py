import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("📊 داشبورد كثافة الفصول - أسوان 2026")

uploaded_file = st.file_uploader("قم برفع ملف الإحصاء", type=["csv"])

if uploaded_file is not None:
    # 1. حل مشكلة الترميز
    encodings = ['utf-8-sig', 'windows-1256', 'cp1256']
    df = None
    for enc in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc, header=None)
            break
        except:
            continue

    if df is not None:
        try:
            # تنظيف الصفوف التي تحتوي على فواصل فارغة فقط
            df = df.dropna(how='all', axis=0)
            
            # 2. البحث عن صف البيانات (يبدأ من الصف الذي يحتوي على كلمة أسوان)
            # سنقوم بتصفية الصفوف التي تحتوي على اسم إدارة تعليمية حقيقية
            keywords = ['أسوان', 'دراو', 'نصر', 'كوم أمبو', 'إدفو']
            
            extracted_data = []
            for _, row in df.iterrows():
                row_list = row.dropna().tolist()
                # التحقق إذا كان الصف يحتوي على اسم إدارة في بدايته
                if any(k in str(row.values) for k in keywords):
                    # استخلاص: الاسم (أول نص)، الفصول (الرقم قبل الأخير)، التلاميذ (آخر رقم)
                    name = [str(x) for x in row.values if any(k in str(x) for k in keywords)][0]
                    # استخراج الأرقام فقط من الصف
                    nums = [pd.to_numeric(x, errors='coerce') for x in row.values if pd.notnull(x)]
                    nums = [x for x in nums if not pd.isna(x)]
                    
                    if len(nums) >= 2:
                        extracted_data.append({
                            'الإدارة': name,
                            'الفصول': nums[-2], # قبل الأخير
                            'التلاميذ': nums[-1] # الأخير
                        })

            final_df = pd.DataFrame(extracted_data)

            if not final_df.empty:
                # 3. العمليات الحسابية
                final_df['الكثافة'] = final_df['التلاميذ'] / final_df['الفصول']
                threshold = 40 # حد التحذير

                # --- العرض ---
                st.success("تم استخراج البيانات بنجاح!")
                
                # كروت الإحصاء
                c1, c2, c3 = st.columns(3)
                c1.metric("إجمالي التلاميذ", f"{int(final_df['التلاميذ'].sum()):,}")
                c2.metric("إجمالي الفصول", f"{int(final_df['الفصول'].sum()):,}")
                c3.metric("متوسط الكثافة", f"{final_df['الكثافة'].mean():.1f}")

                # الرسم البياني
                st.subheader("📈 مؤشر كثافة الفصول حسب الإدارة")
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = ['#ff4b4b' if x > threshold else '#00cc96' for x in final_df['الكثافة']]
                sns.barplot(data=final_df, x='الإدارة', y='الكثافة', palette=colors, ax=ax)
                ax.axhline(threshold, color='#31333f', linestyle='--', label='حد الأمان')
                plt.xticks(rotation=45)
                st.pyplot(fig)

                # الجدول الملون
                st.subheader("⚠️ جدول المتابعة والتحذير")
                def style_density(v):
                    color = 'red' if v > threshold else 'green'
                    return f'color: {color}; font-weight: bold'

                st.dataframe(final_df.style.applymap(style_density, subset=['الكثافة']))
            else:
                st.error("لم يتم العثور على بيانات الإدارات داخل الملف. تأكد من صحة أسماء الإدارات.")

        except Exception as e:
            st.error(f"خطأ في معالجة المحتوى: {e}")
