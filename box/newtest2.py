import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service  # 新增：用於服務管理
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


################################
#
# 店家列表下滑次數
scroll_times = 35
#
# 評論區下滑次數
scroll_times_review = 200
#
# 每抓取 time_sleep 家店後休息30秒
time_sleep = 10
#
################################


# 設置 WebDriver（使用新版 Selenium 初始化方式）
service = Service(ChromeDriverManager().install())  # 自動下載並設置 ChromeDriver
driver = webdriver.Chrome(service=service)  # 初始化 WebDriver
wait = WebDriverWait(driver, 10)  # 設置顯式等待時間

# 儲存店家基本資訊和評論
data = []
data_reviews = {}

# 滾動評論區的函數
def scroll_reviews_section():
    try:
        review_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//button[@aria-label="撰寫評論"]')
        ))

        # 獲取按鈕的位置和尺寸
        location = review_button.location
        size = review_button.size
        x = location['x'] + size['width'] / 2
        y = location['y'] * 2 + size['height'] / 2

        # 移動滑鼠到「撰寫評論」按鈕
        pyautogui.moveTo(x, y, duration=0.5)
        print("鼠標已移動到「撰寫評論」按鈕位置")

        # 在按鈕位置滾動
        for i in range(scroll_times_review):
            pyautogui.scroll(-10000)  # 向下滾動
            time.sleep(1)  # 等待評論載入

        print("完成評論區滾動")
    except Exception as e:
        print(f"評論區滾動失敗：{e}")

# 點擊評論全文按鈕的函數
def click_expand_buttons():
    try:
        full_text_buttons = driver.find_elements(By.XPATH, '//button[@class="w8nwRe kyuRq"]')
        for index, button in enumerate(full_text_buttons, start=1):
            try:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(0.5)
                print(f"已成功點擊展開全文按鈕：第 {index} 個")
            except (ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException) as e:
                print(f"無法點擊展開全文按鈕：{e}")
                continue
    except Exception as e:
        print(f"展開全文按鈕點擊失敗：{e}")

# 抓取評論文字的函數
def scrape_reviews():
    reviews = []
    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='MyEned']")))
    review_elements = driver.find_elements(By.XPATH, "//div[@class='MyEned']/span[@class='wiI7pd']")
    for element in review_elements:
        try:
            review_text = element.text
            reviews.append(review_text)
            time.sleep(0.1)
        except Exception as e:
            print(f"抓取評論失敗: {e}")
    return reviews

# 保存資料到 CSV 文件的函數
def save_data_to_csv(data, reviews_dict):
    df = pd.DataFrame(data)
    df.to_csv('all_stores.csv', index=False, encoding='utf-8-sig')
    print("店家基本信息已保存至 all_stores.csv")

    for store_name, reviews in reviews_dict.items():
        reviews_df = pd.DataFrame(reviews, columns=['評論'])
        file_name = f"{store_name}.csv"
        
        # 清理檔案名稱中的無效字元
        file_name = ''.join(c if c not in '\\/:*?"<>|' else '_' for c in file_name)
        
        reviews_df.to_csv(file_name, index=False, encoding='utf-8-sig')
        print(f"{store_name} 的評論已保存至 {file_name}")

# 打開 Google Maps
driver.get("https://www.google.com/maps")
time.sleep(2)

# 搜索______區的酒吧(可自行修改)
search_box = driver.find_element(By.ID, "searchboxinput")
search_box.send_keys("深坑區 酒吧")
search_box.send_keys(Keys.ENTER)
time.sleep(5)

# 找到左側結果列表的滾動區域
results_container = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))

def scrape_store_links(driver, results_container):
    links = []
    for _ in range(scroll_times):
        driver.execute_script("arguments[0].scrollTop += 5000;", results_container)
        time.sleep(2)

    store_elements = driver.find_elements(By.XPATH, '//a[@class="hfpxzc"]')
    for store in store_elements:
        try:
            link = store.get_attribute("href")
            print(f"鏈接: {link}")
            links.append(link)
        except Exception as e:
            print(f"抓取鏈接失敗: {e}")
            continue
    return links

def extract_store_info(driver, link):
    try:
        store_name = wait.until(EC.visibility_of_element_located((By.XPATH, '//h1'))).text
        print(f"店名: {store_name}")

        try:
            rating_text = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//span[@role="img" and contains(@aria-label, "顆星")]')
            )).get_attribute("aria-label")
            rating = rating_text.replace(" 顆星", "")
        except:
            rating = "評分未找到"
        print(f"評分: {rating}")

        try:
            review_count = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//span[contains(@aria-label, "則評論")]')
            )).get_attribute("aria-label").replace("則評論", "").strip()
        except:
            review_count = "評論數未找到"
        print(f"評論數: {review_count}")

        try:
            address = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//button[contains(@data-item-id, "address")]')
            )).text.lstrip(" ").strip()
        except:
            address = "地址未找到"
        print(f"地址: {address}")

        return {
            "店名": store_name,
            "評分": rating,
            "評論數": review_count,
            "地址": address,
            "鏈接": link
        }

    except Exception as e:
        print(f"抓取店家資訊失敗: {e}")
        return None

def visit_links_and_extract_info(driver, links):
    data = []
    ii = 0
    for link in links:
        try:
            driver.get(link)
            print(f"訪問中: {link}")
            time.sleep(2)
            store_info = extract_store_info(driver, link)
            if store_info:
                data.append(store_info)

                # 打開評論區並抓取評論
                try:
                    reviews_button = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, '//button[@role="tab" and (contains(@aria-label, "評論") or contains(@aria-label, "Reviews"))]')
                    ))
                    reviews_button.click()
                    print("成功點擊評論按鈕")
                    time.sleep(2)

                    # 滾動評論區以加載更多評論
                    scroll_reviews_section()

                    # 展開評論並抓取評論內容
                    click_expand_buttons()
                    all_reviews = scrape_reviews()
                    data_reviews[store_info["店名"]] = all_reviews
                    for idx, review in enumerate(all_reviews, 1):
                        print(f"評論 {idx}: {review}")
                except Exception as e:
                    print(f"無法抓取評論：{e}")
                ii += 1
                if ii % time_sleep == 0:
                    time.sleep(30)
        except Exception as e:
            print(f"訪問鏈接失敗: {link}, 原因: {e}")
            continue
    return data

# 抓取所有店家連結
store_links = scrape_store_links(driver, results_container)

# 訪問每個連結並抓取基本資訊及評論
store_data = visit_links_and_extract_info(driver, store_links)

# 保存到 CSV 文件
save_data_to_csv(store_data, data_reviews)

# 關閉瀏覽器
driver.quit()