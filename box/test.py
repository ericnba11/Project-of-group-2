from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import random

# 設置 WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
driver = webdriver.Chrome(options=options)

# 儲存店家和評論資料
data = []

def get_store_elements():
    """重新獲取店家元素列表"""
    return driver.find_elements(By.XPATH, '//a[@class="hfpxzc"]')

def scroll_and_load(results_container, scrolls=20):
    """模擬滾動和隨機操作以載入更多內容"""
    for _ in range(scrolls):
        driver.execute_script("arguments[0].scrollTop += 1500;", results_container)
        time.sleep(random.uniform(3, 6))

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

    # 設置目標店家數量
    max_stores = 10
    processed_stores = 0

    while processed_stores < max_stores:
        # 滾動並加載更多店家
        scroll_and_load(results_container, scrolls=10)
        store_elements = get_store_elements()

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

                # 點擊評論按鈕進入評論區
                try:
                    reviews_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[@role="tab" and contains(@aria-label, "評論")]'))
                    )
                    reviews_button.click()
                    print("成功點擊評論按鈕")
                    time.sleep(3)  # 等待評論頁面加載

                    # 滾動評論區以加載更多評論
                    scrollable_reviews = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@class="m6QErb DxyBCb kA9KIf dS8AEf"]'))
                    )
                    for _ in range(5):  # 控制滾動次數
                        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_reviews)
                        time.sleep(2)  # 等待加載評論

                    # 抓取前五則評論
                    reviews_data = []
                    review_elements = driver.find_elements(By.XPATH, '//div[@class="wiI7pd"]')
                    for review in review_elements[:5]:  # 抓取前五則評論
                        reviews_data.append(review.text)
                        print(f"評論: {review.text}")

                    # 將店家及評論資料加入至 data
                    data.append({
                        "店名": store_name,
                        "評分": rating,
                        "地址": address,
                        "電話": phone,
                        "鏈接": store_link,
                        "評論": reviews_data
                    })

                except Exception as e:
                    print(f"無法點擊評論按鈕或抓取評論：{e}")

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
    df.to_csv('xinyi_bars_reviews.csv', index=False, encoding='utf-8-sig')
    print("資料已成功儲存至 xinyi_bars_reviews.csv")
