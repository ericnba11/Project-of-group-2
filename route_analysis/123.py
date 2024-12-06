import googlemaps

# 初始化 Google Maps API 客戶端
API_KEY = "AIzaSyDCLj84_0snA421SRH9hvpznoB5kSM4P4I"  # 請替換為你的 API 金鑰
gmaps = googlemaps.Client(key=API_KEY)


def get_user_location():
    """
    使用 Google Geolocation API 獲取使用者的當前位置
    """
    try:
        # 使用 Geolocation API 獲取使用者的地理位置
        result = gmaps.geolocate()
        location = result["location"]
        lat, lng = location["lat"], location["lng"]
        return {"lat": lat, "lng": lng}
    except Exception as e:
        print(f"無法獲取使用者位置: {e}")
        return None


def find_nearby_places_by_keyword(latitude, longitude, keyword, radius=1000):
    """
    使用 Google Places API 根據關鍵字搜尋使用者當前位置附近的地點
    """
    try:
        # 呼叫 places API 搜尋附近的地點
        response = gmaps.places(
            query=keyword,
            location=(latitude, longitude),
            radius=radius
        )
        results = response.get("results", [])

        # 擷取前 10 間地點資訊
        places = []
        for result in results[:10]:
            name = result.get("name", "Unknown")
            address = result.get("formatted_address", "Unknown location")
            rating = result.get("rating", "No rating")
            places.append({
                "name": name,
                "address": address,
                "rating": rating,
            })
        return places
    except Exception as e:
        print(f"搜尋附近地點時發生錯誤: {e}")
        return None


# 主程序
if __name__ == "__main__":
    # 獲取使用者當前位置
    user_location = get_user_location()
    if user_location:
        print(f"使用者位置: {user_location}")
        latitude = user_location["lat"]
        longitude = user_location["lng"]

        # 使用「酒吧」關鍵字搜尋附近地點
        keyword = "酒吧"
        places = find_nearby_places_by_keyword(latitude, longitude, keyword)
        if places:
            print("\n附近的酒吧:")
            for idx, place in enumerate(places, 1):
                print(f"{idx}. {place['name']}")
                print(f"   地址: {place['address']}")
                print(f"   評分: {place['rating']}\n")
        else:
            print("找不到附近的酒吧")
    else:
        print("未能定位使用者位置")
