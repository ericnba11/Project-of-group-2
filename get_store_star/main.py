from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
import re


# 定義爬取單一店家評論的函數
def scrape_single_store(store_link, scroll_times_review, file_name):
    # 初始化 WebDriver
    chrome_service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    wait = WebDriverWait(driver, 10)

    # 訪問店家連結
    driver.get(store_link)
    time.sleep(2)

    # 點擊評論按鈕
    try:
        reviews_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class, "Gpq6kf") and contains(text(), "評論")]')
            )
        )
        reviews_button.click()
        print("成功點擊評論按鈕")
        time.sleep(2)
    except Exception as e:
        print(f"無法點擊評論按鈕: {e}")
        driver.quit()
        return

    # 滾動評論區的函數
    def scroll_reviews_section():
        try:
            review_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//span[contains(text(),"撰寫評論") and contains(@class, "GMtm7c")]')
                )
            )

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
                pyautogui.scroll(-5000)  # 向下滾動
                time.sleep(0.5)  # 等待評論載入

            print("完成評論區滾動")
        except Exception as e:
            print(f"評論區滾動失敗：{e}")

    # 點擊「展開全文」按鈕的函數
    def click_expand_buttons():
        try:
            expand_buttons = driver.find_elements(
                By.XPATH, '//button[@class="w8nwRe kyuRq"]'
            )
            for index, button in enumerate(expand_buttons, start=1):
                try:
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.1)
                except Exception:
                    continue
            print("已點擊所有「展開全文」按鈕")
        except Exception as e:
            print(f"點擊「展開全文」按鈕失敗：{e}")

    def scrape_reviews():
        reviews_data = []
        try:
            # 找到所有評論區塊
            review_blocks = driver.find_elements(By.XPATH, '//div[contains(@class, "jftiEf fontBodyMedium")]')
            for index, block in enumerate(review_blocks, start=1):
                try:
                    # 抓取評論文本
                    try:
                        review_text = block.find_element(By.XPATH, './/span[contains(@class, "wiI7pd")]').text
                    except Exception as e:
                        print(f"第 {index} 條評論無法抓取，設為預設值：{e}")
                        review_text = "未提供評論"

                    # 抓取評分並提取數字部分
                    try:
                        star_rating_element = block.find_element(
                            By.XPATH, './/span[@role="img" and contains(@aria-label, "顆星")]'
                        )
                        star_rating_text = star_rating_element.get_attribute("aria-label")  # 獲取完整的 aria-label 文本
                        star_rating = int(star_rating_text.split(" ")[0])  # 提取「顆星」前的數字
                    except Exception as e:
                        print(f"第 {index} 條評分無法抓取，設為預設值：{e}")
                        star_rating = None  # 若抓不到評分，設為 None

                    # 抓取發布時間並提取數字部分
                    try:
                        time_element = block.find_element(By.XPATH, './/span[contains(@class, "rsqaWe")]')
                        time_text = time_element.text  # 獲取完整發布時間文本（例如 "1 個月前"）
                        time_value = int(re.search(r'\d+', time_text).group())  # 提取數字部分
                    except Exception as e:
                        print(f"第 {index} 條發布時間無法抓取，設為預設值：{e}")
                        time_value = None  # 若抓不到發布時間，設為 None

                    # 添加評論、評分和發布時間至數據結構
                    reviews_data.append({"評論": review_text, "評分": star_rating, "發布時間(個月前)": time_value})
                except Exception as e:
                    print(f"抓取第 {index} 條評論失敗：{e}")
                    continue
            print(f"共抓取到 {len(reviews_data)} 條評論")
            return reviews_data
        except Exception as e:
            print(f"抓取評論失敗：{e}")
            return []

    # 開始滾動評論區並展開全文
    scroll_reviews_section()
    click_expand_buttons()

    # 抓取評論和評分
    all_reviews = scrape_reviews()

    # 保存到 CSV 文件
    df = pd.DataFrame(all_reviews)
    df.to_csv(f"{file_name}.csv", index=False, encoding="utf-8-sig")
    print(f"評論已保存至 {file_name}.csv")

    # 關閉瀏覽器
    driver.quit()


# 主程式
if __name__ == "__main__":
    store_link = input("請輸入店家的 Google Maps 連結：")

    # 輸入檔名
    while True:
        user_filename = input("請輸入檔案名稱（不含副檔名）：")
        sanitized_name = re.sub(r'[<>:"/\\|?*]', "_", user_filename)  # 清理檔名
        if sanitized_name.strip():  # 確保檔名不是空的
            break
        print("檔名無效，請重新輸入！")

    # 輸入滾動次數
    while True:
        try:
            scroll_times_review = int(input("請輸入滾動次數 (正整數)："))
            if scroll_times_review > 0:
                break
            else:
                print("請輸入大於 0 的數字！")
        except ValueError:
            print("無效輸入，請輸入正整數！")

    # 開始爬取評論
    scrape_single_store(store_link, scroll_times_review, sanitized_name)
