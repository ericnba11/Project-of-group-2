from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd  # 用於處理 CSV
import random

# 設置 WebDriver
driver = webdriver.Chrome()

# 儲存店家的資料
data = []

def get_store_elements():
    """重新獲取店家元素列表"""
    return driver.find_elements(By.XPATH, '//a[@class="hfpxzc"]')

try:
    # 打開 Google Maps
    driver.get("https://www.google.com/maps")
    time.sleep(2)  # 等待頁面加載

    # 找到搜尋框並輸入「信義區 酒吧」
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys("信義區 酒吧")
    search_box.send_keys(Keys.ENTER)
    time.sleep(3)  # 等待結果加載

    # 找到左側結果列表的滾動區域
    results_container = driver.find_element(By.XPATH, '//div[@role="feed"]')

    # 滾動左側列表區域，向下滾動多次以加載更多店家
    for _ in range(5):  # 調整滾動次數
        driver.execute_script("arguments[0].scrollTop += 1000;", results_container)
        time.sleep(2)  # 加入延遲以確保內容載入

    # 抓取所有顯示的店家鏈接
    store_elements = get_store_elements()

    # 遍歷每個店家
    for index, store in enumerate(store_elements, start=1):
        try:
            store_name = store.get_attribute("aria-label")  # 抓取店家名稱
            store_link = store.get_attribute("href")  # 抓取店家鏈接
            print(f"\n{index}. 正在處理店家: {store_name}")

            # 點擊該店家的鏈接，進入詳細頁面
            driver.execute_script("arguments[0].click();", store)
            time.sleep(3)  # 等待頁面加載

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

        time.sleep(random.uniform(3, 6))  # 隨機等待3到6秒

        # 返回上一頁
        driver.back()
        time.sleep(5)  # 等待頁面加載返回列表

        # 重新獲取店家元素列表以避免 StaleElementReferenceException
        store_elements = get_store_elements()

finally:
    # 關閉瀏覽器
    driver.quit()

    # 將資料轉換為 DataFrame
    df = pd.DataFrame(data)

    # 儲存為 CSV 檔案
    df.to_csv('xinyi_bars.csv', index=False, encoding='utf-8-sig')
    print("資料已成功儲存至 xinyi_bars.csv")
