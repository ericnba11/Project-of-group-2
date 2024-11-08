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

# 使用 webdriver-manager 自動安裝和管理 chromedriver
driver = webdriver.Chrome(ChromeDriverManager().install())

# 儲存所有店家的基本資訊
all_stores = []
# 儲存每家店的評論
data_reviews = {}

def get_store_elements():
    # 抓取店家列表中的店家鏈接元素
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
                time.sleep(0.5)  # 減少等待時間
                print(f"已成功點擊展開全文按鈕：第 {index} 個")
            except (ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException) as e:
                print(f"無法點擊展開全文按鈕：{e}")
                continue  # 若無法點擊，繼續點擊下一個按鈕
    except Exception as e:
        print(f"展開全文按鈕點擊失敗：{e}")

# 抓取評論文字的函數
def scrape_reviews():
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
            time.sleep(0.5)  # 減少抓取評論時的等待時間
        except Exception as e:
            print(f"抓取評論失敗: {e}")

    return reviews

# 保存資料到 CSV 文件的函數
def save_data_to_csv(data, reviews_dict):
    """
    將店家資料和評論保存為 CSV 文件。
    :param data: 店家基本信息列表
    :param reviews_dict: 每家店家對應的評論字典，鍵為店家名稱，值為評論列表
    """
    # 保存店家基本信息為 CSV 文件
    df = pd.DataFrame(data)
    df.to_csv('all_stores.csv', index=False, encoding='utf-8-sig')
    print("店家基本信息已保存至 all_stores.csv")

    # 保存每家店的評論為單獨的 CSV 文件
    for store_name, reviews in reviews_dict.items():
        reviews_df = pd.DataFrame(reviews, columns=['評論'])
        file_name = f"{store_name}.csv"
        reviews_df.to_csv(file_name, index=False, encoding='utf-8-sig')
        print(f"{store_name} 的評論已保存至 {file_name}")

# 定義一個重試點擊的函數
def click_with_retry(element, retries=3):
    for _ in range(retries):
        try:
            element.click()
            return True
        except Exception:
            time.sleep(1)
    return False

# 第一階段：抓取所有店家基本資訊
try:
    # 打開 Google Maps
    driver.get("https://www.google.com/maps")
    time.sleep(3)  # 減少主頁加載的等待時間

    # 找到搜尋框並輸入「大安區 酒吧」
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys("大安區 酒吧")
    search_box.send_keys(Keys.ENTER)
    time.sleep(3)  # 減少結果加載的等待時間

    # 找到左側結果列表的滾動區域
    results_container = driver.find_element(By.XPATH, '//div[@role="feed"]')

    # 滾動左側列表區域，向下滾動多次以加載更多店家
    for _ in range(50):  # 減少滾動次數
        driver.execute_script("arguments[0].scrollTop += 3000;", results_container)
        time.sleep(1)  # 減少滾動的等待時間

    # 抓取所有顯示的店家鏈接
    store_elements = get_store_elements()

    # 初始化店家索引
    index = 1
    for store in store_elements:
        store_name = store.get_attribute("aria-label")  # 抓取店家名稱
        store_link = store.get_attribute("href")  # 抓取店家鏈接
        print(f"{index}. 正在處理店家: {store_name}")

        # 將店家基本資訊儲存到清單
        all_stores.append({
            "店名": store_name,
            "鏈接": store_link
        })
        index += 1

    # 保存所有店家基本信息至 CSV
    save_data_to_csv(all_stores, {})

except Exception as e:
    print("抓取店家基本資訊失敗:", e)

finally:
    driver.quit()

# 第二階段：利用儲存的鏈接重新抓取評論
# 重新啟動瀏覽器
driver = webdriver.Chrome(ChromeDriverManager().install())

try:
    # 從 CSV 中讀取所有店家的基本信息
    all_stores = pd.read_csv('all_stores.csv').to_dict('records')

    # 迭代每家店的鏈接進行評論抓取
    for index, store in enumerate(all_stores, start=1):
        store_name = store["店名"]
        store_link = store["鏈接"]
        print(f"正在處理第 {index} 家店家: {store_name}")

        # 使用鏈接導航到店家頁面
        driver.get(store_link)
        time.sleep(3)  # 減少頁面加載的等待時間

        # 點擊評論按鈕
        try:
            wait = WebDriverWait(driver, 5)
            reviews_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@role="tab" and (contains(@aria-label, "評論") or contains(@aria-label, "Reviews"))]')))
            click_with_retry(reviews_button, retries=5)
            print("成功點擊評論按鈕")
            time.sleep(2)  # 減少評論頁面加載的等待時間

            # 點擊排序
            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='排序']]")))
                click_with_retry(button, retries=5)
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

            except NoSuchElementException:
                print("未找到排序按鈕")

            # 在該位置滾動
            for i in range(150):  # 減少滾動次數
                pyautogui.scroll(-10000)  # 向下滾動
                time.sleep(1.5)  # 減少滾動等待時間

            # 點擊評論按鈕後，嘗試點擊展開全文的按鈕
            click_expand_buttons()

            # 抓取評論
            all_reviews = scrape_reviews()

            # 儲存每家店的評論
            data_reviews[store_name] = all_reviews

            # 輸出評論結果
            for idx, review in enumerate(all_reviews, 1):
                                print(f"評論 {idx}: {review}")

        except Exception as e:
            print(f"無法點擊評論按鈕：{e}")

        # 隨機等待，以避免被反爬蟲機制偵測
        time.sleep(random.uniform(3, 6))  # 減少隨機等待時間

    # 保存所有店家的評論到個別 CSV 文件
    save_data_to_csv(all_stores, data_reviews)

except Exception as e:
    print("抓取評論過程中發生錯誤：", e)

finally:
    # 關閉瀏覽器
    driver.quit()
