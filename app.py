import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. قراءة البيانات مع ضبط العناوين بناءً على الملف المعدل
# نستخدم skiprows=1 للوصول لأسماء الإدارات مباشرة
df = pd.read_csv('مدارس المديرية وتلاميذ 2026.xlsx - الاحصاء.csv', skiprows=1)

# تنظيف وتسمية الأعمدة الأساسية (الإدارة + أعمدة الإجمالي في نهاية الصف)
# العمود 0: الإدارة، العمود 14: إجمالي المدارس، العمود 15: إجمالي الفصول، العمود 16: إجمالي التلاميذ
df_clean = df.iloc[:, [0, 14, 15, 16]].copy()
df_clean.columns = ['الإدارة', 'إجمالي_مدارس', 'إجمالي_فصول', 'إجمالي_تلاميذ']

# حذف الصفوف التي لا تحتوي على اسم إدارة تعليمية وتحويل الأرقام
df_clean = df_clean.dropna(subset=['الإدارة'])
df_clean[['إجمالي_فصول', 'إجمالي_تلاميذ']] = df_clean[['إجمالي_فصول', 'إجمالي_تلاميذ']].apply(pd.to_numeric)

# 2. حساب متوسط الكثافة (تلميذ لكل فصل)
df_clean['متوسط_الكثافة'] = df_clean['إجمالي_تلاميذ'] / df_clean['إجمالي_فصول']

# 3. ضبط مؤشر التحذير (40 تلميذ هو الحد الأقصى الافتراضي)
threshold = 40
df_clean['مؤشر_التحذير'] = df_clean['متوسط_الكثافة'].apply(lambda x: '🔴 خطر (مرتفعة)' if x > threshold else '🟢 مستقرة')

# عرض النتائج في الجدول
print("--- نتائج تحليل الكثافة الطلابية لعام 2026 ---")
print(df_clean[['الإدارة', 'إجمالي_فصول', 'إجمالي_تلاميذ', 'متوسط_الكثافة', 'مؤشر_التحذير']])

# 4. الرسم البياني للمقارنة بين الإدارات
plt.figure(figsize=(10, 6))
colors = ['#e74c3c' if x > threshold else '#2ecc71' for x in df_clean['متوسط_الكثافة']]

sns.barplot(x='الإدارة', y='متوسط_الكثافة', data=df_clean, palette=colors)
plt.axhline(y=threshold, color='red', linestyle='--', label=f'حد التحذير ({threshold} تلميذ/فصل)')

plt.title('مؤشر كثافة التلاميذ في فصول المديرية - 2026', fontsize=14)
plt.ylabel('متوسط عدد التلاميذ بالفصل الواحد')
plt.xlabel('الإدارة التعليمية')
plt.legend()

# إضافة قيمة الكثافة فوق كل عمود
for i, val in enumerate(df_clean['متوسط_الكثافة']):
    plt.text(i, val + 0.5, f'{val:.1f}', ha='center', fontweight='bold')

plt.tight_layout()
plt.show()
