from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# 設定 Selenium 瀏覽器驅動
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # 如果需要可以移除註解運行無頭模式
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# 滾動以加載更多評論
def scroll_and_load_comments(scrollable_div, scrolls=5):
    """模擬滾動評論區以分批加載評論。"""
    for _ in range(scrolls):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(random.uniform(2, 3))  # 隨機延遲，模仿人為操作

# 主函數 - 抓取多家店家評論
def get_comments(search_query="信義區 酒吧", max_stores=5, max_comments=15):
    search_url = f"https://www.google.com/maps/search/{search_query}"
    driver.get(search_url)
    time.sleep(5)  # 等待頁面加載

    store_data = []

    # 抓取每家店家的評論
    for store_index in range(max_stores):
        # 點擊每個搜尋結果進入店家頁面
        search_results = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
        if store_index >= len(search_results):
            break  # 如果搜尋結果數量不足則停止
        search_results[store_index].click()
        time.sleep(3)  # 等待頁面加載

        # 進入評論區
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[jsaction="pane.reviewChart.moreReviews"]'))
            ).click()
            time.sleep(2)  # 等待評論頁面加載
        except Exception as e:
            print(f"無法進入評論區：{e}")
            continue

        # 滾動評論區並抓取評論
        store_name = driver.title
        comments, authors, ratings = [], [], []
        scrollable_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Google 地圖的評論"]'))
        )

        # 分批滾動並抓取評論
        while len(comments) < max_comments:
            scroll_and_load_comments(scrollable_div, scrolls=2)  # 每次滾動兩次以加載新評論

            # 使用 BeautifulSoup 抓取評論內容
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_elements = soup.select('div.gws-localreviews__google-review')
            
            if not review_elements:
                print("未能找到評論元素，請檢查選擇器是否正確。")
                break
            
            for review in review_elements[len(comments):]:  # 僅抓取新加載的評論
                author = review.select_one('span.X5PpBb').get_text() if review.select_one('span.X5PpBb') else None
                rating = review.select_one('span.KvQ8cc').get("aria-label") if review.select_one('span.KvQ8cc') else None
                comment_text = review.select_one('span[jsname="bN97Pc"]').get_text() if review.select_one('span[jsname="bN97Pc"]') else None
                
                authors.append(author)
                ratings.append(rating)
                comments.append(comment_text)

                # 若達到每家店的最大評論數量則停止
                if len(comments) >= max_comments:
                    break

        # 儲存每家店家的評論數據
        store_data.extend([{"店家名稱": store_name, "作者": a, "評分": r, "評論內容": c} for a, r, c in zip(authors, ratings, comments)])

        # 返回搜尋結果頁面
        driver.back()
        time.sleep(2)  # 等待頁面加載

    # 檢查是否有數據
    if not store_data:
        print("未能成功抓取評論，請檢查程式設置。")
    else:
        # 將所有評論儲存至 DataFrame 並匯出至 CSV
        all_reviews = pd.DataFrame(store_data)
        output_path = 'C:/Users/USER/Desktop/study group 2_box/box/信義區酒吧評論.csv'
        all_reviews.to_csv(output_path, index=False, encoding='utf-8-sig')
        print("成功將評論儲存至 '信義區酒吧評論.csv'")

    driver.quit()

# 執行主程式
get_comments(search_query="信義區 酒吧", max_stores=5, max_comments=15)
