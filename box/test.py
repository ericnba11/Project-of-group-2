from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd  # 用於處理 CSV
import random

# 設置 WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
driver = webdriver.Chrome(options=options)

# 儲存店家的資料
data = []

def get_store_elements():
    """重新獲取店家元素列表"""
    return driver.find_elements(By.XPATH, '//a[@class="hfpxzc"]')

def scroll_and_load(results_container, scrolls=20):
    """模擬滾動和隨機操作以載入更多內容"""
    for _ in range(scrolls):
        driver.execute_script("arguments[0].scrollTop += 1500;", results_container)
        time.sleep(random.uniform(3, 6))  # 增加隨機等待時間

        # 偶爾點擊空白處或滾回頂部模擬使用者行為
        if random.random() < 0.2:
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(1, 3))

try:
    # 打開 Google Maps
    driver.get("https://www.google.com/maps")
    time.sleep(random.uniform(2, 5))

    # 找到搜尋框並輸入「信義區 酒吧」
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys("信義區 酒吧")
    search_box.send_keys(Keys.ENTER)
    time.sleep(random.uniform(3, 6))

    # 找到左側結果列表的滾動區域
    results_container = driver.find_element(By.XPATH, '//div[@role="feed"]')

    # 進行分段滾動與分批抓取
    max_stores = 10
    processed_stores = 0

    while processed_stores < max_stores:
        # 滾動並加載更多店家
        scroll_and_load(results_container, scrolls=10)
        store_elements = get_store_elements()  # 重新獲取更新後的店家列表

        while processed_stores < max_stores and processed_stores < len(store_elements):
            store = store_elements[processed_stores]
            try:
                store_name = store.get_attribute("aria-label")
                store_link = store.get_attribute("href")
                print(f"\n{processed_stores + 1}. 正在處理店家: {store_name}")

                # 點擊該店家的鏈接，進入詳細頁面
                driver.execute_script("arguments[0].click();", store)
                time.sleep(random.uniform(3, 6))

                # 抓取店家詳細資訊
                rating = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//span[@class="MW4etd"]'))
                ).text

                # 先檢查地址元素是否存在
                try:
                    address = driver.find_element(By.XPATH, '//button[@data-item-id="address"]').text
                except Exception:
                    address = "地址未找到"

                # 先檢查電話元素是否存在
                try:
                    phone = driver.find_element(By.XPATH, '//button[@data-item-id="phone"]').text
                except Exception:
                    phone = "電話未找到"

                # 將資料儲存到列表中
                data.append({
                    "店名": store_name,
                    "評分": rating,
                    "地址": address,
                    "電話": phone,
                    "鏈接": store_link
                })

            except Exception as e:
                print("無法取得完整資料，可能是元素未找到。", e)

            processed_stores += 1
            time.sleep(random.uniform(3, 6))

            # 返回上一頁
            driver.back()
            time.sleep(random.uniform(4, 7))

            # 每次返回後重新獲取店家元素列表
            store_elements = get_store_elements()

finally:
    driver.quit()
    df = pd.DataFrame(data)
    df.to_csv('xinyi_bars.csv', index=False, encoding='utf-8-sig')
    print("資料已成功儲存至 xinyi_bars.csv")
