import pandas as pd
from googletrans import Translator
import os

i = 0  # 成功翻譯的文件數量
f = 0  # 失敗的翻譯數量
t = 0  # 成功翻譯的評論數量

# 初始化翻译器
translator = Translator()

# 指定目标文件夹路径
folder_path = r"C:\Users\USER\Desktop\study group 2_box\台北市\文山區 酒吧"  # 修改為你的本地資料夾路徑
output_folder_path = r"C:\Users\USER\Desktop\study group 2_box\台北市\文山區 酒吧_translated"  # 輸出翻譯後文件的資料夾

if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# 遍历文件夹中的 CSV 文件
for file_name in os.listdir(folder_path):
    if file_name.endswith(".csv"):  # 检查是否是 CSV 文件
        file_path = os.path.join(folder_path, file_name)  # 获取完整路径
        print(f"正在处理文件：{file_name}")

        # 读取 CSV 文件
        df = pd.read_csv(file_path)

        # 检查是否存在 "評論" 列
        if "評論" not in df.columns:
            print(f"文件 {file_name} 中没有 '評論' 列，跳过。")
            continue

        # 翻译每条评论
        translations = []
        for text in df["評論"]:
            try:
                # 翻译评论
                translation = translator.translate(str(text), dest="en")
                translations.append(translation.text)
                t += 1
            except Exception as e:
                # 翻译失败，保留原文本
                print(f"翻译失败：{text}，错误信息：{e}")
                translations.append(text)
                f += 1

        # 创建新的 DataFrame
        new_df = pd.DataFrame({
            "Original": df["評論"],
            "EN": translations
        })

        # 保存翻译结果为新文件
        output_file_name = os.path.splitext(file_name)[0] + "_translated.csv"
        output_file_path = os.path.join(output_folder_path, output_file_name)
        new_df.to_csv(output_file_path, index=False)
        print(f"已保存翻译文件：{output_file_path}")

        i += 1
        print("-" * 10 + "已處理第" + str(i) + "間酒吧" + "-" * 10)
        print("此間酒吧翻譯成功比率：" + str(t / (t + f) * 100) + "%")  # 修正了此處的計算