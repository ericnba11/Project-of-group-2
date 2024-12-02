import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 設定中文字體
rcParams['font.sans-serif'] = ['Microsoft JhengHei']
rcParams['axes.unicode_minus'] = False

# 檔案路徑
stars_file = r"C:\Users\USER\Desktop\study group 2_box\折線柱狀圖\WTNC_星星.csv"
compound_file = r"C:\Users\USER\Desktop\study group 2_box\台北市\信義區 酒吧_final\WTNC_final.csv"

# 店家名稱
shop_name = "信義區 BAR24"

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

# 修正情感分析分數映射到 1~5 星等
def map_to_stars(compound):
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

merged_df['compound_group'] = merged_df['Compound'].apply(map_to_stars)

# 計算星等分布比例
star_counts = stars_df['評分'].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
star_ratios = star_counts / star_counts.sum()

# 計算情感分析分布比例
compound_counts = merged_df['compound_group'].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
compound_ratios = compound_counts / compound_counts.sum()

# 打印情感分析分數最低的 10 則評論及其對應的 Google Maps 星等與評論
lowest_10_comments = merged_df.nsmallest(10, 'Compound')[['評論', '評分', 'Compound']]
print("情感分析分數最低的 10 則評論及其對應的 Google Maps 星等：")
print(lowest_10_comments)

# 可視化
plt.figure(figsize=(12, 6))

# 繪製星等分布的比例柱狀圖
plt.bar(star_ratios.index, star_ratios.values, color='green', alpha=0.7, label='Google Maps 星等分布比例')

# 繪製情感分析分布的比例柱狀圖
plt.bar(compound_ratios.index, compound_ratios.values, color='blue', alpha=0.5, label='情感分析分布比例')

# 添加標籤與圖例
plt.xlabel('星等分數 / 情感分析分組')
plt.ylabel('比例')
plt.xticks(ticks=[1, 2, 3, 4, 5], labels=['1', '2', '3', '4', '5'])
plt.title(f'{shop_name} - 星等分布與情感分析分布比例對比')
plt.legend()

# 顯示圖表
plt.show()
