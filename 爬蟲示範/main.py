from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

# 打開目標網址
url = "https://aca.nccu.edu.tw/zh/%E7%A2%A9%E5%8D%9A%E5%A3%AB%E7%8F%AD/%E5%85%A5%E5%AD%B8%E9%80%9A%E7%9F%A5"
driver.get(url)

# 等待頁面加載（可以根據實際需要調整時間）
time.sleep(3)

# 抓取頁面上所有文字
page_text = driver.find_element(By.TAG_NAME, "body").text

# 印出抓取到的文字
print(page_text)

# 關閉瀏覽器
driver.quit()
