from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# 設置 WebDriver
driver = webdriver.Chrome()

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

    # 滾動左側列表區域，向下滾動 5 次作為示例
    for _ in range(10):
        # 滾動列表，讓 Google Maps 加載更多結果
        driver.execute_script("arguments[0].scrollTop += 600;", results_container)
        time.sleep(1)  # 加入延遲以確保內容載入

    # 抓取所有顯示的店家名稱
    store_elements = driver.find_elements(By.XPATH, '//a[@class="hfpxzc"]')

    # 將店家名稱列出來
    for index, store in enumerate(store_elements, start=1):
        store_name = store.get_attribute("aria-label")  # 抓取 aria-label 中的名稱
        print(f"{index}. {store_name}")

finally:
    # 關閉瀏覽器
    driver.quit()
