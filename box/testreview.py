from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import emoji
import re
import time

# 設定 Selenium 瀏覽器驅動
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# 根據店家名搜尋並提取店家 ID
def get_store_ids(search_query="信義區 酒吧", max_stores=5):
    search_url = f"https://www.google.com/maps/search/{search_query}"
    driver.get(search_url)
    time.sleep(5)  # 等待頁面加載

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 提取符合店家格式的 ID
    store_ids = set(re.findall(r'0x.{16}:0x.{16}', str(soup)))  # 抓取 "0x...:0x..." 格式的店家 ID
    store_ids = list(store_ids)[:max_stores]  # 只保留指定數量的店家

    return store_ids

# 使用 API 抓取評論
def get_comment(store_id, max_comments=5):
    store_id_list = store_id.split(':')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    }

    # 設置 API URL
    url1 = f"https://www.google.com.tw/maps/preview/review/listentitiesreviews?authuser=0&hl=zh-TW&gl=tw&authuser=0&pb=!1m2!1y{store_id_list[0]}!2y{store_id_list[1]}!2m2!1i"
    url3 = "!2i10!3e1!4m5!3b1!4b1!5b1!6b1!7b1!5m2!1s!7e81"

    作者, 評論內容, 評分 = [], [], []

    for i in range(0, max_comments):
        try:
            url2 = i * 10
            url = url1 + str(url2) + url3
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print(f"資料獲取錯誤，狀態碼: {response.status_code}")
                break

            text = response.text.replace(')]}\'', '')
            text = emoji.demojize(text)
            data = json.loads(text)

            if isinstance(data, list) and len(data) > 2:
                reviews = data[2]
                for review in reviews:
                    評論內容.append(str(review[3]).replace('\n', '') if len(review) > 3 else None)
                    作者.append(review[0][1] if review[0] and len(review[0]) > 1 else None)
                    評分.append(review[4] if len(review) > 4 else None)

            if len(評論內容) >= max_comments:
                break

        except Exception as e:
            print(f"發生錯誤: {e}")
            break

    # 確保所有欄位長度相同
    min_length = min(len(作者), len(評分), len(評論內容))
    return pd.DataFrame({
        "店家 ID": [store_id] * min_length,
        "作者": 作者[:min_length],
        "評分": 評分[:min_length],
        "評論內容": 評論內容[:min_length]
    })

# 主程式 - 搜尋並抓取多家店的評論
store_ids = get_store_ids()
all_reviews = pd.DataFrame()

for store_id in store_ids:
    store_reviews = get_comment(store_id, max_comments=5)
    all_reviews = pd.concat([all_reviews, store_reviews], ignore_index=True)

# 儲存至 CSV
output_path = 'C:/Users/USER/Desktop/study group 2_box/box/sinyi_bars_reviews.csv'
all_reviews.to_csv(output_path, index=False, encoding='utf-8-sig')
print("成功將評論儲存至 'sinyi_bars_reviews.csv'")
driver.quit()
