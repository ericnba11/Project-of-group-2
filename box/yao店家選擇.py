import pandas as pd
import googlemaps

# 初始化 Google Maps API 客戶端
API_KEY = "AIzaSyDCLj84_0snA421SRH9hvpznoB5kSM4P4I"  # 替換為你的 API 金鑰
gmaps = googlemaps.Client(key=API_KEY)


# 使用 Google Geolocation API 獲取使用者位置
def get_user_location():
    """
    使用 Google Geolocation API 獲取使用者的當前位置
    """
    try:
        result = gmaps.geolocate()  # Geolocation API 請求
        location = result["location"]
        return {"lat": location["lat"], "lng": location["lng"]}
    except Exception as e:
        print(f"無法獲取使用者位置: {e}")
        return None


# 使用 Google Places API 搜尋
def find_bars_by_keyword(latitude, longitude, keyword="酒吧", radius=1000, top_n=20):
    """
    使用 Google Places API 搜尋指定位置附近的酒吧，根據關鍵字返回前 N 家結果
    """
    try:
        response = gmaps.places_nearby(
            location=(latitude, longitude),
            radius=radius,
            keyword=keyword
        )
        results = response.get("results", [])

        # 提取前 N 家酒吧的名稱
        bars = [{"name": result["name"]} for result in results[:top_n]]
        return bars
    except Exception as e:
        print(f"搜尋酒吧時發生錯誤: {e}")
        return []


# 載入已合併的酒吧資料
def load_combined_bars_data(file_path):
    """
    讀取已合併的酒吧資料
    """
    try:
        bars_data = pd.read_csv(file_path, encoding="utf-8")
        return bars_data
    except Exception as e:
        print(f"讀取酒吧資料時發生錯誤: {e}")
        return None


# 比對 Google Places 酒吧與本地資料
def match_bars(places_bars, bars_data):
    """
    比對 Google Places 的搜尋結果與本地 bars 資料，返回匹配的酒吧
    """
    bars_data["店名"] = bars_data["店名"].str.strip()  # 去除名稱前後空白
    matched_bars = []
    for place in places_bars:
        match = bars_data[bars_data["店名"] == place["name"]]
        if not match.empty:
            matched_bars.append({
                "name": place["name"],
                "address": match.iloc[0]["地址"],  # 從本地資料中獲取地址
                "rating": match.iloc[0]["評分"]  # 從本地資料中獲取評分
            })
    return matched_bars


# 主程式
if __name__ == "__main__":
    # 1. 定位使用者位置
    user_location = get_user_location()
    if not user_location:
        print("無法定位使用者位置，請檢查 API 設置。")
        exit()
    print(f"使用者位置: {user_location}")

    # 2. 使用 Google Places API 搜尋酒吧
    places_bars = find_bars_by_keyword(user_location["lat"], user_location["lng"], keyword="酒吧", radius=1000,
                                       top_n=20)
    print(f"找到 {len(places_bars)} 間酒吧（來自 Google Places API）")

    # 3. 載入已合併的酒吧資料
    combined_bars_path = r"C:\Users\USER\Desktop\study group 2_box\User__Place\combined_bars.csv"  # 已合併的檔案路徑
    bars_data = load_combined_bars_data(combined_bars_path)
    if bars_data is None:
        print("無法載入酒吧資料，程式結束。")
        exit()
    print(f"已載入 {len(bars_data)} 間酒吧資料（來自已合併的資料）")

    # 4. 比對 Google Places 結果與本地資料
    matched_bars = match_bars(places_bars, bars_data)
    print(f"有 {len(matched_bars)} 間酒吧同時出現在 Google Places 和本地資料中")

    # 5. 輸出匹配結果
    print("\n匹配的酒吧列表:")
    for idx, bar in enumerate(matched_bars, 1):
        print(f"{idx}. {bar['name']} - 地址: {bar['address']} - 評分: {bar['rating']}")
