import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 設定中文字體
rcParams['font.sans-serif'] = ['Microsoft JhengHei']
rcParams['axes.unicode_minus'] = False

# 檔案路徑
stars_file = r"C:\Users\USER\Desktop\study group 2_box\深入比較圖\去斯萬家 chez Swann by Jumi Tavern_star.csv"
compound_file = r"C:\Users\USER\Desktop\study group 2_box\台北市\大安區 酒吧_final\去斯萬家 chez Swann by Jumi Tavern_final.csv"

# 店家名稱
shop_name = "去斯萬家 chez Swann by Jumi Tavern"

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

# 定義將 Compound 分數轉換為 1~5 的函數
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

# 計算星等分布比例 (Google Maps)
star_counts = stars_df['評分'].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
star_ratios = star_counts / star_counts.sum()

# 計算情感分析分布比例 (Vader 分組)
compound_counts = merged_df['compound_group'].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
compound_ratios = compound_counts / compound_counts.sum()

# 印出情感分析分數最低的 10 則評論
lowest_10_comments = merged_df.nsmallest(10, 'Compound')[['評論', '評分', 'Compound']]
print("情感分析分數最低的 10 則評論及其對應的 Google Maps 星等：")
print(lowest_10_comments)

# 繪圖
plt.figure(figsize=(12, 6))

x = [1, 2, 3, 4, 5]  # x 軸刻度
width = 0.4  # 每個柱狀圖的寬度

# 在X軸上，左側為Google Maps星等的比例，稍微往左偏移 width/2
plt.bar([i - width/2 for i in x], star_ratios.values, width=width, color='green', alpha=0.7, label='Google Maps 星等分布比例')

# 右側為情感分析比例，往右偏移 width/2
plt.bar([i + width/2 for i in x], compound_ratios.values, width=width, color='blue', alpha=0.5, label='情感分析分布比例')

plt.xlabel('星等分數 / 情感分析分組')
plt.ylabel('比例')
plt.title(f'{shop_name} - 星等分布與情感分析分布比例對比')

# 將 x 軸刻度顯示在整數位置
plt.xticks(ticks=x, labels=[str(i) for i in x])

plt.legend()
plt.show()
