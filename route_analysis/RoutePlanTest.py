
import googlemaps

# 初始化 Google Maps API 客戶端
API_KEY = "AIzaSyBpcCbuaebldhTSqCP66rWdbnGumFixt2Q"
gmaps = googlemaps.Client(key=API_KEY)

# 信義區隨意挑的5家酒吧
bar_names = ["196 Bar", "A Glass or Two", "A Light", "Alchemy Bar Taipei", "Bar 浮"]

# 查詢指定酒吧的地點
def get_bar_locations(bar_names):
    locations = []
    for bar in bar_names:
        result = gmaps.places(query=bar)
        if result.get("results"):
            place = result["results"][0]
            locations.append({
                "name": bar,
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"],
            })
        else:
            print(f"未找到酒吧 {bar} 的地點")
    #print("test locations data")
    #print(locations)
    return locations

# 規劃最佳路徑
def get_optimized_route_try_all_endpoints(locations, start_location):
    """
    嘗試 locations 中所有項目作為終點，找出總路徑長最短的方案。
    """
    best_route = None
    best_distance = float("inf")
    best_legs_details = None
    best_total_duration = None

    for i, possible_endpoint in enumerate(locations):
        # 起點
        origin = {"lat": start_location["lat"], "lng": start_location["lng"]}
        # 嘗試的終點
        destination = possible_endpoint
        # 剩下的點作為 waypoints
        waypoints = [loc for j, loc in enumerate(locations) if j != i]

        try:
            # Google Maps Directions API 請求
            routes_result = gmaps.directions(
                origin=f"{origin['lat']},{origin['lng']}",
                destination=f"{destination['lat']},{destination['lng']}",
                mode="walking",
                waypoints=[f"{w['lat']},{w['lng']}" for w in waypoints],
                optimize_waypoints=True
            )

            if routes_result:
                route = routes_result[0]
                optimized_order = route["waypoint_order"]

                # 根據優化順序重新排列 waypoints
                optimized_waypoints = [waypoints[j] for j in optimized_order]
                # 完整路徑：起點 -> 優化的 waypoints -> 終點
                full_route = [{"name": "起點", "lat": origin["lat"], "lng": origin["lng"]}] + \
                             optimized_waypoints + \
                             [{"name": destination["name"], "lat": destination["lat"], "lng": destination["lng"]}]

                # 計算路徑的總距離與各段細節
                total_distance = 0
                total_duration = 0
                legs_details = []
                for leg in route["legs"]:
                    distance = leg["distance"]["value"] / 1000  # 公里
                    duration = leg["duration"]["value"] / 60  # 分鐘
                    transport_mode = recommend_transport_mode(distance, duration)
                    legs_details.append({
                        "start_address": leg["start_address"],
                        "end_address": leg["end_address"],
                        "distance_km": distance,
                        "duration_min": duration,
                        "transport_mode": transport_mode,
                    })
                    total_distance += distance
                    total_duration += duration

                # 比較，保存距離最短的方案
                if total_distance < best_distance:
                    best_distance = total_distance
                    best_route = full_route
                    best_legs_details = legs_details
                    best_total_duration = total_duration

        except Exception as e:
            print(f"嘗試終點 {possible_endpoint['name']} 時發生錯誤: {e}")

    return best_route, best_legs_details, best_distance, best_total_duration

# 
def get_user_location():
    """
    使用 Google Geolocation API 獲取使用者的當前位置
    """
    try:
        # Geolocation API 請求
        result = gmaps.geolocate()
        location = result["location"]
        lat, lng = location["lat"], location["lng"]
        return {"lat": lat, "lng": lng}
    except Exception as e:
        print(f"無法獲取使用者位置: {e}")
        return None

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

# 主程序
if __name__ == "__main__":
    # 指定起點位置
    start_location = get_user_location()
    
    # 獲取酒吧的地點
    bar_locations = get_bar_locations(bar_names)
    if len(bar_locations) < len(bar_names):
        print("部分酒吧地點未找到，請檢查名稱是否正確")
    else:
        # 規劃最佳路徑
        optimized_locations, legs_details, total_distance, total_duration = get_optimized_route_try_all_endpoints(
            bar_locations, start_location
        )
        if optimized_locations:
            print("\n最佳路徑順序:")
            print(f"起點: ({start_location['lat']}, {start_location['lng']})")
            for i, loc in enumerate(optimized_locations):
                print(f"{i+1}. {loc['name']} ({loc['lat']}, {loc['lng']})")
            print(f"終點: {optimized_locations[-1]['name']} ({optimized_locations[-1]['lat']}, {optimized_locations[-1]['lng']})")

            print("\n每段路徑的細節與推薦交通方式:")
            for i, leg in enumerate(legs_details):
                print(f"從 {leg['start_address']} 到 {leg['end_address']}: {leg['distance_km']:.2f} 公里, 約 {leg['duration_min']:.1f} 分鐘")
                print(f"推薦交通方式: {leg['transport_mode']}")

            print(f"\n總距離: {total_distance:.2f} 公里")
            print(f"總時間: {total_duration:.1f} 分鐘")
        else:
            print("無法找到最佳路徑")
