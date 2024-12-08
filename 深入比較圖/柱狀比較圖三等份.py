import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 設定中文字體（若無法顯示中文可略過或使用其他字型）
rcParams['font.sans-serif'] = ['Microsoft JhengHei']
rcParams['axes.unicode_minus'] = False

# 檔案路徑 (請依實際路徑修改)
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

# 將 Compound 分數分類為低中高
def categorize_compound(c):
    if c < -0.3:
        return 'Low'
    elif -0.3 <= c <= 0.3:
        return 'Mid'
    else:
        return 'High'

merged_df['compound_category'] = merged_df['Compound'].apply(categorize_compound)

# 將星等分類為低中高
def categorize_stars(s):
    if s in [1, 2]:
        return 'Low'
    elif s in [3, 4]:
        return 'Mid'
    else: # 5星
        return 'High'

merged_df['star_category'] = merged_df['評分'].apply(categorize_stars)

# 計算各分類比例 (Google Maps 星等)
star_counts = merged_df['star_category'].value_counts()
star_ratios = star_counts / star_counts.sum()

# 計算各分類比例 (情感分析)
compound_counts = merged_df['compound_category'].value_counts()
compound_ratios = compound_counts / compound_counts.sum()

# 若想依序確保順序為 Low, Mid, High，可以重新排序
star_order = ['Low', 'Mid', 'High']
compound_order = ['Low', 'Mid', 'High']

star_ratios = star_ratios.reindex(star_order, fill_value=0)
compound_ratios = compound_ratios.reindex(compound_order, fill_value=0)

# 檢視情感分析分數最低的10則評論
lowest_10_comments = merged_df.nsmallest(10, 'Compound')[['評論', '評分', 'Compound']]
print("情感分析分數最低的 10 則評論及其對應的 Google Maps 星等：")
print(lowest_10_comments)

# 開始繪製柱狀圖
plt.figure(figsize=(12, 6))

x_positions = [1, 2, 3]  # 對應 Low, Mid, High
width = 0.4

# 繪製 Google Maps 星等分布比例(綠色柱狀) 偏左
plt.bar([x - width/2 for x in x_positions], star_ratios.values, width=width, color='green', alpha=0.7, label='Google Maps 星等分布比例')

# 繪製 情感分析分布比例(藍色柱狀) 偏右
plt.bar([x + width/2 for x in x_positions], compound_ratios.values, width=width, color='blue', alpha=0.5, label='情感分析分布比例')

# 設定 X 軸標籤
plt.xticks(ticks=x_positions, labels=['低(Low)', '中(Mid)', '高(High)'])

plt.xlabel('分類群組')
plt.ylabel('比例')
plt.title(f'{shop_name} - 星等與情感分析的低中高分布比例對比')
plt.legend()

plt.show()
