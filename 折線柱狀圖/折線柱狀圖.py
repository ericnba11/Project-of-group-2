import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

# 設定中文字體
rcParams['font.sans-serif'] = ['Microsoft JhengHei']
rcParams['axes.unicode_minus'] = False

# 檔案路徑
stars_file = r"C:\Users\USER\Desktop\study group 2_box\折線柱狀圖\深杯子概念店 La Copa Oscura_星星.csv"
compound_file = r"C:\Users\USER\Desktop\study group 2_box\台北市\北投區 酒吧_final\深杯子概念店 La Copa Oscura_final.csv"

# 讀取資料
stars_df = pd.read_csv(stars_file, encoding='utf-8')
compound_df = pd.read_csv(compound_file, encoding='utf-8')

# 合併資料
merged_df = pd.merge(
    stars_df[['評論', '評分']],
    compound_df[['Original', 'Compound']],
    left_on='評論', right_on='Original',
    how='inner'
)

# 打印最高分與最低分
max_compound = merged_df['Compound'].max()
min_compound = merged_df['Compound'].min()
print(f"情感分析分數 (Compound) 的最高分是: {max_compound}")
print(f"情感分析分數 (Compound) 的最低分是: {min_compound}")

# 修正 Compound 分數映射到 1~5 星等
def map_to_stars(compound):
    # 按 -1 到 1 的區間分層對應到星等
    if compound < -0.6:
        return 1
    elif -0.6 <= compound < -0.2:
        return 2
    elif -0.2 <= compound < 0.2:
        return 3
    elif 0.2 <= compound < 0.6:
        return 4
    else:
        return 5

merged_df['mapped_stars'] = merged_df['Compound'].apply(map_to_stars)

# 視覺化
plt.figure(figsize=(12, 6))

# 繪製星等分布柱狀圖
sns.histplot(
    data=stars_df, x='評分',
    bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
    kde=False, color='blue', alpha=0.7, label='星等分布'
)
plt.xlabel('星等分數')
plt.ylabel('評論數量')
plt.xticks(ticks=[1, 2, 3, 4, 5], labels=['1', '2', '3', '4', '5'])
plt.title('星等分布與情感分析真實分布')

# 使用第二個 Y 軸繪製散點圖
plt.twinx()
sns.stripplot(
    data=merged_df, x='mapped_stars', y='Compound',
    alpha=0.5, color='orange', jitter=0.2, label='情感分析分數'
)
plt.ylabel('情感分析分數 (Compound)')

# 加入圖例
plt.legend(loc='upper right')

# 顯示圖表
plt.tight_layout()
plt.show()
