import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="تحليل كثافات أسوان", layout="wide")
st.title("📊 لوحة مؤشرات الكثافة الطلابية - 2026")

uploaded_file = st.file_uploader("قم برفع ملف الإحصاء", type=["csv"])

if uploaded_file is not None:
    # 1. تجربة الترميز العربي
    df = None
    for enc in ['utf-8-sig', 'windows-1256', 'cp1256']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc, header=None)
            break
        except:
            continue

    if df is not None:
        try:
            # 2. استخراج البيانات بذكاء
            extracted_rows = []
            # أسماء الإدارات المتوقع وجودها في الملف
            target_admins = ['أسوان', 'دراو', 'نصر', 'كوم أمبو', 'إدفو', 'أدفو'] 

            for _, row in df.iterrows():
                # تحويل الصف لنص واحد للبحث فيه
                row_str = " ".join(row.astype(str).values)
                
                for admin in target_admins:
                    if admin in row_str:
                        # استخراج الأرقام فقط من هذا الصف
                        nums = []
                        for val in row.values:
                            try:
                                # تنظيف الرقم من الفواصل أو المسافات
                                clean_val = str(val).replace(',', '').strip()
                                n = float(clean_val)
                                if n > 0: nums.append(n)
                            except:
                                continue
                        
                        # في ملفك: آخر رقمين هما دائماً (الفصول، التلاميذ)
                        if len(nums) >= 2:
                            extracted_rows.append({
                                'الإدارة': admin,
                                'الفصول': nums[-2],
                                'التلاميذ': nums[-1]
                            })
                        break

            final_df = pd.DataFrame(extracted_rows).drop_duplicates(subset=['الإدارة'])

            if not final_df.empty:
                # 3. الحسابات
                final_df['الكثافة'] = final_df['التلاميذ'] / final_df['الفصول']
                threshold = 40

                # --- العرض المرئي ---
                st.success(f"تم العثور على بيانات لـ {len(final_df)} إدارات تعليمية")
