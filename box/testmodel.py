from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException
import pyautogui
import time
import pandas as pd  # 用於處理 CSV
import random
from webdriver_manager.chrome import ChromeDriverManager

# 設置 WebDriver，使用 webdriver-manager 自動管理 chromedriver
driver = webdriver.Chrome()

# 儲存店家的資料
data = []
visited_stores = set()  # 用於追蹤已抓取過的店家鏈接

def get_store_elements():
    """
    重新獲取店家元素列表
    """
    return driver.find_elements(By.XPATH, '//a[@class="hfpxzc"]')

# 點擊評論全文按鈕的函數
def click_expand_buttons():
    try:
        # 獲取所有展開全文的按鈕
        full_text_buttons = driver.find_elements(By.XPATH, '//button[@class="w8nwRe kyuRq"]')

        for index, button in enumerate(full_text_buttons, start=1):
            try:
                # 使用 JavaScript 點擊展開全文按鈕
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)  # 等待展開後的內容加載
                print(f"已成功點擊展開全文按鈕：第 {index} 個")
            except (ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException) as e:
                print(f"無法點擊展開全文按鈕：{e}")
                continue  # 若無法點擊，繼續點擊下一個按鈕
            time.sleep(1)

    except Exception as e:
        print(f"展開全文按鈕點擊失敗：{e}")

def scrape_reviews():
    """抓取評論文字"""
    reviews = []

    # 等待評論加載完成
    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='MyEned']")))

    # 獲取所有評論元素
    review_elements = driver.find_elements(By.XPATH, "//div[@class='MyEned']/span[@class='wiI7pd']")

    for element in review_elements:
        try:
            # 抓取評論的文字內容
            review_text = element.text
            reviews.append(review_text)
            time.sleep(1)
        except Exception as e:
            print(f"抓取評論失敗: {e}")

    return reviews

try:
    # 打開 Google Maps
    driver.get("https://www.google.com/maps")
    time.sleep(2)  # 等待頁面加載

    # 找到搜尋框並輸入「信義區 酒吧」
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys("信義區 酒吧")
    search_box.send_keys(Keys.ENTER)
    time.sleep(1.5)  # 等待結果加載

    # 找到左側結果列表的滾動區域
    results_container = driver.find_element(By.XPATH, '//div[@role="feed"]')

    # 持續滾動左側列表區域，直到不再加載新店家
    previous_length = 0
    max_scroll_attempts = 50  # 增加滾動次數上限
    scroll_attempts = 0

    while scroll_attempts < max_scroll_attempts:
        # 重新獲取結果列表的滾動區域以避免 StaleElementReferenceException
        results_container = driver.find_element(By.XPATH, '//div[@role="feed"]')
        store_elements = get_store_elements()
        current_length = len(store_elements)

        if current_length == previous_length:
            scroll_attempts += 1  # 如果沒有新增店家，增加滾動計數
        else:
            scroll_attempts = 0  # 如果新增了店家，重置計數
            previous_length = current_length

        driver.execute_script("arguments[0].scrollTop += 1000;", results_container)
        time.sleep(2)  # 增加滾動間隔，以確保列表有時間加載更多內容

    print(f"總共顯示出 {len(store_elements)} 家店家")

    # 抓取所有顯示的店家鏈接
    store_elements = get_store_elements()

    for index in range(len(store_elements)):
        # 使用 try-except 來避免 StaleElementReferenceException 錯誤
        try:
            if index < len(store_elements):
                store = store_elements[index]
                store_name = store.get_attribute("aria-label")  # 抓取店家名稱
                store_link = store.get_attribute("href")  # 抓取店家鏈接

                # 檢查店家是否已處理過
                if store_link in visited_stores:
                    print(f"已抓取過的店家：{store_name}, 跳過...")
                    continue
                else:
                    visited_stores.add(store_link)  # 新店家則加入追蹤集合
                    print(f"{index + 1}. 店名: {store_name}, 鏈接: {store_link}")

            else:
                print(f"索引超出範圍，第 {index + 1} 個店家已不可用")
                continue

        except StaleElementReferenceException:
            # 若元素過期，重新獲取元素列表並檢查索引範圍
            print(f"元素失效，在第 {index + 1} 家店家時重新獲取元素列表")
            store_elements = get_store_elements()
            if index < len(store_elements):
                store = store_elements[index]
                store_name = store.get_attribute("aria-label")
                store_link = store.get_attribute("href")

                # 檢查店家是否已處理過
                if store_link in visited_stores:
                    print(f"已抓取過的店家：{store_name}, 跳過...")
                    continue
                else:
                    visited_stores.add(store_link)
                    print(f"{index + 1}. 店名: {store_name}, 鏈接: {store_link}")
            else:
                print(f"重獲失敗，索引超出範圍")
                continue

        # 點擊該店家的鏈接，進入詳細頁面
        driver.execute_script("arguments[0].click();", store)
        time.sleep(2)  # 等待頁面加載

        # 抓取店家詳細資訊
        try:
            # 使用 WebDriverWait 等待元素加載
            rating = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@role="main"]//span[@aria-hidden="true"]'))
            ).text

            # 先檢查地址元素是否存在
            try:
                address = driver.find_element(By.XPATH, '//button[@data-item-id="address"]').text
            except NoSuchElementException:
                address = "地址未找到"

            # 先檢查電話元素是否存在
            try:
                phone = driver.find_element(By.XPATH, '//button[@data-item-id="phone"]').text
            except NoSuchElementException:
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

        # 點擊評論按鈕
        try:
            wait = WebDriverWait(driver, 1)
            reviews_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@role="tab" and (contains(@aria-label, "評論") or contains(@aria-label, "Reviews"))]')
            ))
            reviews_button.click()
            print("成功點擊評論按鈕")
            time.sleep(1)  # 等待評論頁面加載

            # 點擊排序
            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='排序']]")))
                button.click()
                time.sleep(1)
                # 等待“最相關”按鈕可被點擊
                most_relevant_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='fxNQSd' and @data-index='0']//div[text()='最相關']")))
                driver.execute_script("arguments[0].click();", most_relevant_button)
                time.sleep(1)

                # 找到按鈕的坐標位置
                location = button.location
                size = button.size
                x = location['x'] + size['width'] / 2
                y = location['y'] + size['height'] / 2

                # 將鼠標移動到該坐標
                pyautogui.moveTo(x, y, duration=0.5)

                # 在該位置滾動
                for i in range(15):
                    pyautogui.scroll(-2000)  # 向下滾動
                    time.sleep(random.uniform(2, 3))  # 隨機延遲
            except NoSuchElementException:
                print("未找到排序按钮")

            # 點擊評論按鈕後，嘗試點擊展開全文的按鈕
            click_expand_buttons()

            time.sleep(3)

            # 抓取評論
            all_reviews = scrape_reviews()

            # 輸出評論結果
            for idx, review in enumerate(all_reviews, 1):
                print(f"評論 {idx}: {review}")

        except Exception as e:
            print(f"無法點擊評論按鈕：{e}")

        time.sleep(random.uniform(3, 6))  # 隨機等待3到6秒

        # 返回上一頁
        driver.back()
        time.sleep(5)  # 等待頁面加載返回列表

        # 重新滾動和獲取店家元素列表以避免 StaleElementReferenceException
        for _ in range(5):  # 滾動多次以確保列表加載完整
            results_container = driver.find_element(By.XPATH, '//div[@role="feed"]')  # 每次滾動前重新獲取元素
            driver.execute_script("arguments[0].scrollTop += 1000;", results_container)
            time.sleep(1)
        store_elements = get_store_elements()

finally:
    # 關閉瀏覽器前，輸出已爬取的店家數量
    print(f"成功爬取的店家數量：{len(data)}")
    driver.quit()
