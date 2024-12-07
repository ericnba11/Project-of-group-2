# 初始化 Google Maps API 客戶端
import googlemaps
import openpyxl

API_KEY = "AIzaSyBpcCbuaebldhTSqCP66rWdbnGumFixt2Q"  # 替換為你的 API 密鑰
gmaps = googlemaps.Client(key=API_KEY)

# 從 Excel 資料庫中讀取酒吧名稱與評分
def load_bar_database_from_excel(file_path):
    """
    從 Excel 文件中讀取酒吧資料庫。
    第一欄為酒吧名稱，第二欄為評分分數。
    """
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
    """
    使用 Google Places API 搜索指定位置附近的酒吧。
    """
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
    """
    從附近的酒吧中篩選出在資料庫中的酒吧，並按評分排序。
    """
    matched_bars = [
        {**bar, "score": database[bar["name"]]} for bar in nearby_bars if bar["name"] in database
    ]
    sorted_bars = sorted(matched_bars, key=lambda x: x["score"], reverse=True)
    return sorted_bars[:top_n]

# 規劃最佳路徑
def get_optimized_route_with_return_to_start(locations, start_location):
    """
    將起點作為終點，規劃最佳路徑。
    """
    try:
        # 將起點加到 waypoints 中，並使用 optimize_waypoints 進行優化
        waypoints = locations
        routes_result = gmaps.directions(
            origin=f"{start_location['lat']},{start_location['lng']}",
            destination=f"{start_location['lat']},{start_location['lng']}",
            mode="walking",
            waypoints=[f"{w['lat']},{w['lng']}" for w in waypoints],
            optimize_waypoints=True
        )

        if routes_result:
            route = routes_result[0]
            optimized_order = route["waypoint_order"]

            # 根據優化順序重新排列 waypoints
            optimized_waypoints = [waypoints[j] for j in optimized_order]
            # 完整路徑：起點 -> 優化的 waypoints -> 起點
            full_route = [{"name": "起點", "lat": start_location["lat"], "lng": start_location["lng"]}] + \
                         optimized_waypoints + \
                         [{"name": "終點 (回到起點)", "lat": start_location["lat"], "lng": start_location["lng"]}]

            return full_route, route["legs"]
        else:
            print("無法找到路徑")
            return None, None
    except Exception as e:
        print(f"規劃路徑時發生錯誤: {e}")
        return None, None

# 根據距離與時間推薦交通方式
def recommend_transport_mode(distance_km, duration_min):
    """
    根據距離和時間推薦交通方式。
    """
    if distance_km <= 2:
        return "步行 (Walking)"
    elif 2 < distance_km <= 10:
        return "騎車 (Bicycling)"
    elif distance_km > 10:
        if duration_min / distance_km < 10:  # 時速大於 6 公里
            return "駕車 (Driving)"
        else:
            return "公共交通 (Transit)"
    return "未知 (Unknown)"

# 計算點對點的距離、時間與交通方式
def calculate_point_to_point_details(route_legs):
    """
    計算每段路徑的距離、時間，以及推薦交通方式。
    """
    details = []
    for leg in route_legs:
        distance_km = leg["distance"]["value"] / 1000  # 公里
        duration_min = leg["duration"]["value"] / 60  # 分鐘
        transport_mode = recommend_transport_mode(distance_km, duration_min)
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
    # 從 Excel 文件載入資料庫
    database_path = "C:/code/git_file/信義區酒吧評分.xlsx"  # 替換為你的 Excel 文件路徑
    bar_database = load_bar_database_from_excel(database_path)

    # 指定起點經緯度
    start_lat = 25.033
    start_lng = 121.564427
    start_location = {"lat": start_lat, "lng": start_lng}

    print(f"起點位置: 經度 {start_location['lng']}, 緯度 {start_location['lat']}")

    # 搜索附近酒吧
    nearby_bars = find_nearby_bars(start_location)
    if not nearby_bars:
        print("附近沒有找到任何酒吧")
    else:
        # 比對資料庫並選出最高分的酒吧
        top_bars = get_top_bars_from_database(nearby_bars, bar_database)
        if not top_bars:
            print("附近的酒吧沒有匹配到資料庫中的酒吧")
        else:
            print("選出的最高分的酒吧:")
            for bar in top_bars:
                print(f"{bar['name']}: {bar['score']} 分")

            # 規劃最佳路徑
            optimized_route, route_legs = get_optimized_route_with_return_to_start(top_bars, start_location)

            if optimized_route and route_legs:
                print("\n最佳路徑順序:")
                for i, loc in enumerate(optimized_route):
                    print(f"{i+1}. {loc['name']} ({loc['lat']}, {loc['lng']})")

                # 計算點對點距離、時間與推薦交通方式
                point_to_point_details = calculate_point_to_point_details(route_legs)

                print("\n每段路徑的細節與推薦交通方式:")
                for i, detail in enumerate(point_to_point_details):
                    print(f"從 {detail['start_address']} 到 {detail['end_address']}:")
                    print(f"  距離: {detail['distance_km']:.2f} 公里")
                    print(f"  時間: {detail['duration_min']:.1f} 分鐘")
                    print(f"  推薦交通方式: {detail['transport_mode']}")
            else:
                print("無法找到最佳路徑")
