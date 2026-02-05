import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. تحميل وتجهيز البيانات
file_path = 'مدارس المديرية وتلاميذ 2026.xlsx - الاحصاء.csv'
# تخطي الصفوف الخمسة الأولى للوصول للبيانات الفعلية
df = pd.read_csv(file_path, skiprows=5)

# تسمية الأعمدة بناءً على هيكل الملف المرفق
df.columns = [
    'Unnamed', 'الإدارة', 
    'رسمي_مدارس', 'رسمي_فصول', 'رسمي_تلاميذ',
    'تجريبي_مدارس', 'تجريبي_فصول', 'تجريبي_تلاميذ',
    'يابانية_مدارس', 'يابانية_فصول', 'يابانية_تلاميذ',
    'خاصة_مدارس', 'خاصة_فصول', 'خاصة_تلاميذ',
    'إجمالي_مدارس', 'إجمالي_فصول', 'إجمالي_تلاميذ', 'Unnamed_end'
]

# تنظيف البيانات وحذف الصفوف الفارغة أو الإجمالية النهائية
df = df.dropna(subset=['الإدارة']).copy()
numeric_cols = ['إجمالي_فصول', 'إجمالي_تلاميذ']
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# 2. حساب متوسط الكثافة (تلميذ/فصل)
df['متوسط_الكثافة'] = df['إجمالي_تلاميذ'] / df['إجمالي_فصول']

# 3. نظام مؤشر التحذير (Threshold = 40)
threshold = 40
df['حالة_الكثافة'] = df['متوسط_الكثافة'].apply(lambda x: '⚠️ خطر (مرتفع)' if x > threshold else '✅ آمن')

# --- العرض الإحصائي ---
print("### تحليل كثافات الفصول حسب الإدارة التعليمية ###")
print(df[['الإدارة', 'إجمالي_فصول', 'إجمالي_تلاميذ', 'متوسط_الكثافة', 'حالة_الكثافة']].to_string(index=False))

# --- الرسم البياني ---
plt.figure(figsize=(12, 6))
sns.set_style("whitegrid")

# رسم الأعمدة
colors = ['red' if x > threshold else 'skyblue' for x in df['متوسط_الكثافة']]
ax = sns.barplot(x='الإدارة', y='متوسط_الكثافة', data=df, palette=colors)

# إضافة خط تحذير
plt.axhline(y=threshold, color='red', linestyle='--', label=f'حد التحذير ({threshold} تلميذ/فصل)')

plt.title('مقارنة متوسط كثافة الفصول حسب الإدارة التعليمية - 2026', fontsize=14)
plt.xlabel('الإدارة التعليمية', fontsize=12)
plt.ylabel('متوسط عدد التلاميذ في الفصل الواحد', fontsize=12)
plt.legend()

# إضافة الأرقام فوق الأعمدة
for p in ax.patches:
    ax.annotate(format(p.get_height(), '.1f'), 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha = 'center', va = 'center', 
                xytext = (0, 9), 
                textcoords = 'offset points')

plt.show()
