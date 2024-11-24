import pandas as pd
from googletrans import Translator
import os
import time
import random
import logging
import chardet
from requests.exceptions import RequestException

# 配置日誌記錄
logging.basicConfig(
    filename="translation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)

# 初始化翻譯器
translator = Translator()

# 指定目標文件夾路徑
folder_path = r"C:/Users/USER/Desktop/study group 2_box/台北市/大安區 酒吧"
output_folder_path = r"C:/Users/USER/Desktop/study group 2_box/台北市/大安區 酒吧_translated"

if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# 自動檢測文件編碼
def detect_encoding(file_path):
    """檢測文件編碼"""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']

# 翻譯函數
def translate_comment(text):
    """翻譯單條評論，包含重試機制和檢查"""
    text = str(text) if text else ""
    if text.strip():
        attempts = 3  # 最多重試次數
        for attempt in range(attempts):
            try:
                time.sleep(random.uniform(0.2, 0.5))  # 隨機延遲
                translation = translator.translate(text, dest="en")
                if translation.text.strip() == text.strip() and attempt < attempts - 1:
                    # 如果翻譯結果與原文相同，嘗試重試
                    continue
                logging.info(f"翻譯成功：{text} -> {translation.text}")
                return translation.text, False  # 翻譯成功，標記為不需要審核
            except Exception as e:
                logging.error(f"翻譯失敗（第 {attempt + 1} 次）：{text}，錯誤信息：{e}")
                if attempt == attempts - 1:
                    return text, True  # 最後一次嘗試失敗，保留原文並標記為需要審核
    else:
        logging.info(f"保留純空白評論：{text}")
        return text, False  # 對於空白評論，不需要審核

# 遍歷文件夾中的 CSV 文件
i = 0  # 成功翻譯的文件數量
f = 0  # 失敗的翻譯數量
t = 0  # 成功翻譯的評論數量

for file_name in os.listdir(folder_path):
    if file_name.endswith(".csv"):  # 檢查是否是 CSV 文件
        file_path = os.path.join(folder_path, file_name)

        # 檢查是否已經存在翻譯後的文件
        output_file_name = os.path.splitext(file_name)[0] + "_translated.csv"
        output_file_path = os.path.join(output_folder_path, output_file_name)

        if os.path.exists(output_file_path):
            print(f"檔案 {output_file_name} 已存在，跳過處理。")
            logging.info(f"檔案 {output_file_name} 已存在，跳過處理。")
            continue  # 跳過該檔案

        print(f"正在處理文件：{file_name}")

        # 檢測文件編碼
        try:
            encoding = detect_encoding(file_path)
            print(f"檔案 {file_name} 使用編碼：{encoding}")
            df = pd.read_csv(file_path, encoding=encoding)
        except Exception as e:
            print(f"無法讀取文件 {file_name}，錯誤信息：{e}")
            logging.error(f"無法讀取文件 {file_name}，錯誤信息：{e}")
            continue

        # 檢查是否存在 "評論" 列
        if "評論" not in df.columns:
            print(f"文件 {file_name} 中沒有 '評論' 列，跳過。")
            logging.warning(f"文件 {file_name} 中沒有 '評論' 列，已跳過。")
            continue

        # 翻譯評論
        translations = []
        needs_review = []
        for text in df["評論"]:
            translated_text, review_flag = translate_comment(text)
            translations.append(translated_text)
            needs_review.append(review_flag)
            if not review_flag:
                t += 1
            else:
                f += 1

        # 保存翻譯結果
        new_df = pd.DataFrame({
            "Original": df["評論"],
            "EN": translations,
            "Needs Review": needs_review
        })

        new_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
        print(f"已保存翻譯文件：{output_file_path}")
        logging.info(f"已保存翻譯文件：{output_file_path}")

        i += 1
        print("-" * 10 + f"已處理第 {i} 間酒吧" + "-" * 10)
        print(f"此間酒吧翻譯成功比率：{t / (t + f) * 100:.2f}%")
        logging.info(f"此間酒吧翻譯成功比率：{t / (t + f) * 100:.2f}%")
