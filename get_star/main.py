import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

################################
#
# 設定搜索區域
district = "信義區 酒吧"
#
# 店家列表下滑次數
scroll_times = 50
#
################################

# 設置 WebDriver
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# 儲存店家基本資訊
data = []

def sanitize_filename(filename):
    # 使用正則表達式，移除所有不允許的字元
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# 修改保存資料到 CSV 文件的函數
def save_data_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"店家基本信息已保存至 {filename}")

# 打開 Google Maps
driver.get("https://www.google.com/maps")
time.sleep(2)

# 搜索區域
search_box = driver.find_element(By.ID, "searchboxinput")
search_box.send_keys(district)
search_box.send_keys(Keys.ENTER)
time.sleep(5)

# 找到左側結果列表的滾動區域
results_container = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))

def scrape_store_links(driver, results_container):
    links = []
    for _ in range(scroll_times):
        driver.execute_script("arguments[0].scrollTop += 3000;", results_container)
        time.sleep(1.5)

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

def scrape_star_ratings():
    star_ratings = {"5星": 0, "4星": 0, "3星": 0, "2星": 0, "1星": 0}
    try:
        # 尋找每個星等的評論數據
        for i in range(5, 0, -1):  # 從 5 星到 1 星
            xpath = f'//tr[@role="img" and contains(@aria-label, "{i} 星級")]'
            element = driver.find_element(By.XPATH, xpath)
            aria_label = element.get_attribute("aria-label")
            count = re.search(r"(\d+) 則評論", aria_label)
            star_ratings[f"{i}星"] = int(count.group(1)) if count else 0
    except Exception as e:
        print(f"抓取星等數據失敗: {e}")
    return star_ratings

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

        # 抓取星等評論數據
        star_ratings = scrape_star_ratings()
        print(f"星等數據: {star_ratings}")

        return {
            "店名": store_name,
            "評分": rating,
            "評論數": review_count,
            "地址": address,
            "鏈接": link,
            **star_ratings  # 將星等數據加入結果
        }

    except Exception as e:
        print(f"抓取店家資訊失敗: {e}")
        return None

def visit_links_and_extract_info(driver, links):
    data = []
    for link in links:
        try:
            driver.get(link)
            print(f"訪問中: {link}")
            time.sleep(2)
            store_info = extract_store_info(driver, link)
            if store_info:
                data.append(store_info)
        except Exception as e:
            print(f"訪問鏈接失敗: {link}, 原因: {e}")
            continue
    return data

# 抓取所有店家連結
store_links = scrape_store_links(driver, results_container)

# 訪問每個連結並抓取基本資訊
store_data = visit_links_and_extract_info(driver, store_links)

# 使用 district 名稱作為檔案名稱
filename = sanitize_filename(district) + ".csv"

# 保存到 CSV 文件
save_data_to_csv(store_data, filename)

# 關閉瀏覽器
driver.quit()
