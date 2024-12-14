# 初始化 Google Maps API 客戶端
import googlemaps
import openpyxl

API_KEY = "AIzaSyBpcCbuaebldhTSqCP66rWdbnGumFixt2Q"  # 替換為你的 API 密鑰
gmaps = googlemaps.Client(key=API_KEY)

# 從地址獲取經緯度
def geocode_address(address):
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]["geometry"]["location"]
            return {"lat": location["lat"], "lng": location["lng"]}
        else:
            print(f"無法找到地址: {address}")
            return None
    except Exception as e:
        print(f"地理編碼失敗: {e}")
        return None

# 從 Excel 資料庫中讀取酒吧名稱與評分
def load_bar_database_from_excel(file_path):
    database = {}
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        for row in sheet.iter_rows(min_row=2, values_only=True):  # 跳過標題列
            name, score = row
            if name and isinstance(score, (int, float)):
                database[name] = score
        print("成功載入資料庫！")
    except Exception as e:
        print(f"載入資料庫時發生錯誤: {e}")
    return database

# 獲取周圍酒吧的地點
def find_nearby_bars(location, radius=2000, keyword="酒吧"):
    try:
        response = gmaps.places_nearby(
            location=f"{location['lat']},{location['lng']}",
            radius=radius,
            keyword=keyword,
            type="bar"
        )
        if response.get("results"):
            bars = []
            for place in response["results"]:
                bars.append({
                    "name": place["name"],
                    "lat": place["geometry"]["location"]["lat"],
                    "lng": place["geometry"]["location"]["lng"],
                })
            return bars
        else:
            print("未找到附近的酒吧")
            return []
    except Exception as e:
        print(f"無法搜索附近酒吧: {e}")
        return []

# 比對資料庫中的酒吧並選出最高分的五家
def get_top_bars_from_database(nearby_bars, database, top_n=5):
    matched_bars = [
        {**bar, "score": database[bar["name"]]} for bar in nearby_bars if bar["name"] in database
    ]
    sorted_bars = sorted(matched_bars, key=lambda x: x["score"], reverse=True)
    return sorted_bars[:top_n]

# 規劃最佳路徑
def get_optimized_route_with_end_point(locations, start_location, end_location):
    try:
        waypoints = locations
        routes_result = gmaps.directions(
            origin=f"{start_location['lat']},{start_location['lng']}",
            destination=f"{end_location['lat']},{end_location['lng']}",
            mode="walking",
            waypoints=[f"{w['lat']},{w['lng']}" for w in waypoints],
            optimize_waypoints=True
        )

        if routes_result:
            route = routes_result[0]
            optimized_order = route["waypoint_order"]
            optimized_waypoints = [waypoints[j] for j in optimized_order]
            full_route = [{"name": "起點", "lat": start_location["lat"], "lng": start_location["lng"]}] + \
                         optimized_waypoints + \
                         [{"name": "終點", "lat": end_location["lat"], "lng": end_location["lng"]}]
            return full_route, route["legs"]
        else:
            print("無法找到路徑")
            return None, None
    except Exception as e:
        print(f"規劃路徑時發生錯誤: {e}")
        return None, None

# 根據距離推薦交通方式
def recommend_transport_mode(distance_km):
    if distance_km <= 1:
        return "步行 (Walking)"
    else:
        return "搭乘大眾運輸 (Public Transit)"

# 計算點對點的距離、時間與交通方式
def calculate_point_to_point_details(route_legs):
    details = []
    for leg in route_legs:
        distance_km = leg["distance"]["value"] / 1000  # 公里
        duration_min = leg["duration"]["value"] / 60  # 分鐘
        transport_mode = recommend_transport_mode(distance_km)
        details.append({
            "distance_km": distance_km,
            "duration_min": duration_min,
            "transport_mode": transport_mode,
            "start_address": leg["start_address"],
            "end_address": leg["end_address"],
        })
    return details


# 主程序
if __name__ == "__main__":
    # 步驟 1: 從 Excel 文件載入酒吧資料庫
    database_path = "C:/code/git_file/台北市酒吧評分.xlsx"  # 替換為你的 Excel 文件路徑
    bar_database = load_bar_database_from_excel(database_path)

    # 步驟 2: 使用者輸入起點地址，並將其轉換為經緯度
    start_address = input("請輸入起點地址: ")
    start_location = geocode_address(start_address)
    if not start_location:  # 如果地理編碼失敗，終止程式
        print("無法獲取起點經緯度，程式結束")
        exit()

    # 步驟 3: 使用者輸入終點地址，並將其轉換為經緯度
    end_address = input("請輸入終點地址: ")
    end_location = geocode_address(end_address)
    if not end_location:  # 如果地理編碼失敗，終止程式
        print("無法獲取終點經緯度，程式結束")
        exit()

    # 顯示起點與終點的地理資訊
    print(f"起點位置: {start_address} -> 經度 {start_location['lng']}, 緯度 {start_location['lat']}")
    print(f"終點位置: {end_address} -> 經度 {end_location['lng']}, 緯度 {end_location['lat']}")

    # 步驟 4: 使用者輸入搜索半徑（單位: 公尺）
    try:
        radius = int(input("請輸入搜索半徑（單位: 公尺，預設 2000 公尺）: "))
        if radius <= 0:  # 如果輸入的半徑無效，使用預設值 2000 公尺
            print("無效的半徑值，將使用預設值 2000 公尺")
            radius = 2000
    except ValueError:  # 如果輸入不是數字，使用預設值 2000 公尺
        print("輸入非數字，將使用預設值 2000 公尺")
        radius = 2000

    # 步驟 5: 搜索起點附近的酒吧
    nearby_bars = find_nearby_bars(start_location, radius=radius)
    if not nearby_bars:  # 如果未找到酒吧，終止流程
        print("附近沒有找到任何酒吧")
    else:
        # 步驟 6: 使用者輸入要選擇的酒吧數量
        try:
            top_n = int(input("請輸入想要選取的酒吧數量: "))
            if top_n <= 0:  # 如果輸入的數量無效，使用預設值 5
                print("無效的數量值，將使用預設值 5")
                top_n = 5
        except ValueError:  # 如果輸入不是數字，使用預設值 5
            print("輸入非數字，將使用預設值 5")
            top_n = 5

        # 從資料庫中匹配找到的酒吧，並選出使用者指定數量的最高分酒吧
        top_bars = get_top_bars_from_database(nearby_bars, bar_database, top_n=top_n)
        if not top_bars:  # 如果附近酒吧無法匹配資料庫，終止流程
            print("附近的酒吧沒有匹配到資料庫中的酒吧")
        else:
            # 顯示選出的最高分酒吧
            print("選出的最高分的酒吧:")
            for bar in top_bars:
                print(f"{bar['name']}: {bar['score']} 分")

            # 步驟 7: 規劃包含起點、終點與選中酒吧的最佳路徑
            optimized_route, route_legs = get_optimized_route_with_end_point(top_bars, start_location, end_location)

            if optimized_route and route_legs:
                # 顯示最佳路徑順序
                print("\n最佳路徑順序:")
                for i, loc in enumerate(optimized_route):
                    print(f"{i+1}. {loc['name']} ({loc['lat']}, {loc['lng']})")

                # 步驟 8: 計算每段路徑的細節與推薦交通方式
                point_to_point_details = calculate_point_to_point_details(route_legs)

                # 顯示每段路徑的詳細資訊
                print("\n每段路徑的細節與推薦交通方式:")
                for i, detail in enumerate(point_to_point_details):
                    print(f"從 {detail['start_address']} 到 {detail['end_address']}:")
                    print(f"  距離: {detail['distance_km']:.2f} 公里")
                    print(f"  時間: {detail['duration_min']:.1f} 分鐘")
                    print(f"  推薦交通方式: {detail['transport_mode']}")
            else:
                # 如果無法找到最佳路徑，給出提示
                print("無法找到最佳路徑")