from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException
import pyautogui
import time
import pandas as pd
import random
from webdriver_manager.chrome import ChromeDriverManager

# 設置 WebDriver
driver = webdriver.Chrome()

# 儲存店家的資料
data = []
# 儲存每家店的評論
data_reviews = {}


# 滾動左側商店列表並抓取所有商店的連結
def get_all_store_links():
    store_links = set()
    results_container = driver.find_element(By.XPATH, '//div[@role="feed"]')

    while True:
        store_elements = driver.find_elements(By.XPATH, '//a[@class="hfpxzc"]')
        for store in store_elements:
            store_link = store.get_attribute("href")
            store_links.add(store_link)

        previous_count = len(store_links)
        driver.execute_script("arguments[0].scrollTop += 1000;", results_container)
        time.sleep(2)
        current_count = len(store_links)

        if current_count == previous_count:
            break

    return list(store_links)


# 點擊評論全文按鈕的函數
def click_expand_buttons():
    try:
        full_text_buttons = driver.find_elements(By.XPATH, '//button[@class="w8nwRe kyuRq"]')
        for index, button in enumerate(full_text_buttons, start=1):
            try:
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
                print(f"已成功點擊展開全文按鈕：第 {index} 個")
            except (ElementClickInterceptedException, StaleElementReferenceException, NoSuchElementException) as e:
                print(f"無法點擊展開全文按鈕：{e}")
                continue
            time.sleep(0.5)
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
            time.sleep(0.5)
        except Exception as e:
            print(f"抓取評論失敗: {e}")

    return reviews


# 抓取店家詳細資訊
def fetch_store_details():
    try:
        store_name = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//h1[contains(@class, "fontHeadlineLarge")]'))
        ).text

        try:
            rating = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//span[contains(@aria-label, "顆星") or contains(@aria-label, "stars")]')
                )
            ).text
        except Exception:
            rating = "評分未找到"

        try:
            address = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//button[contains(@data-item-id, "address")] | //span[contains(@aria-label, "address")]')
                )
            ).text
        except Exception:
            address = "地址未找到"

        try:
            phone = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//button[contains(@data-item-id, "phone")] | //span[contains(@aria-label, "phone")]')
                )
            ).text
        except Exception:
            phone = "電話未找到"

        data.append({
            "店名": store_name,
            "評分": rating,
            "地址": address,
            "電話": phone,
            "鏈接": driver.current_url
        })

        print({
            "店名": store_name,
            "評分": rating,
            "地址": address,
            "電話": phone,
            "鏈接": driver.current_url
        })

    except Exception as e:
        print("無法取得完整資料，可能是元素未找到。", e)


# 保存資料到 CSV 文件的函數
def save_data_to_csv(data, reviews_dict):
    df = pd.DataFrame(data)
    df.to_csv('all_stores.csv', index=False, encoding='utf-8-sig')
    print("店家基本信息已保存至 all_stores.csv")

    for store_name, reviews in reviews_dict.items():
        reviews_df = pd.DataFrame(reviews, columns=['評論'])
        file_name = f"{store_name}.csv"
        reviews_df.to_csv(file_name, index=False, encoding='utf-8-sig')
        print(f"{store_name} 的評論已保存至 {file_name}")


try:
    driver.get("https://www.google.com/maps")
    time.sleep(2)

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys("台北市 酒吧")
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)

    results_container = driver.find_element(By.XPATH, '//div[@role="feed"]')
    for _ in range(10):
        driver.execute_script("arguments[0].scrollTop += 1000;", results_container)
        time.sleep(2)
    all_store_links = get_all_store_links()
    print(f"共抓取到 {len(all_store_links)} 家店家的鏈接")

    for index, store_link in enumerate(all_store_links, start=1):
        driver.get(store_link)
        time.sleep(2)
        fetch_store_details()

        try:
            wait = WebDriverWait(driver, 1)
            reviews_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 '//button[@role="tab" and (contains(@aria-label, "評論") or contains(@aria-label, "Reviews"))]')
            ))
            reviews_button.click()
            print("成功點擊評論按鈕")
            time.sleep(2)

            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='排序']]")))
                button.click()
                time.sleep(1)
                most_relevant_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class='fxNQSd' and @data-index='0']//div[text()='最相關']")))
                driver.execute_script("arguments[0].click();", most_relevant_button)
                time.sleep(1)
            except NoSuchElementException:
                print("未找到排序按鈕")

            for i in range(10):
                pyautogui.scroll(-1000)
                time.sleep(2)

            click_expand_buttons()
            time.sleep(5)

            all_reviews = scrape_reviews()
            data_reviews[store_name] = all_reviews

            for idx, review in enumerate(all_reviews, 1):
                print(f"評論 {idx}: {review}")

        except Exception as e:
            print(f"無法點擊評論按鈕：{e}")

        time.sleep(random.uniform(3, 6))

finally:
    driver.quit()
    save_data_to_csv(data, data_reviews)
