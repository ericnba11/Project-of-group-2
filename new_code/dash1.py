import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import googlemaps

# 初始化 Google Maps API 客戶端
API_KEY = "AIzaSyDCLj84_0snA421SRH9hvpznoB5kSM4P4I"
gmaps = googlemaps.Client(key=API_KEY)

# 載入已合併的酒吧資料
def load_combined_bars_data(file_path):
    try:
        bars_data = pd.read_csv(file_path, encoding="utf-8")
        return bars_data
    except Exception as e:
        print(f"讀取酒吧資料時發生錯誤: {e}")
        return None

# 使用 Google Places API 搜尋
def find_bars_by_keyword(latitude, longitude, keyword="酒吧", radius=1000, top_n=20):
    try:
        response = gmaps.places_nearby(
            location=(latitude, longitude),
            radius=radius,
            keyword=keyword
        )
        results = response.get("results", [])
        bars = [{"name": result["name"], "lat": result["geometry"]["location"]["lat"],
                 "lng": result["geometry"]["location"]["lng"]} for result in results[:top_n]]
        return bars
    except Exception as e:
        print(f"搜尋酒吧時發生錯誤: {e}")
        return []

# 比對 Google Places 酒吧與本地資料
def match_bars(places_bars, bars_data):
    bars_data["店名"] = bars_data["店名"].str.strip()
    matched_bars = []
    for place in places_bars:
        match = bars_data[bars_data["店名"] == place["name"]]
        if not match.empty:
            matched_bars.append({
                "name": place["name"],
                "lat": place["lat"],
                "lng": place["lng"],
                "address": match.iloc[0]["地址"],
                "rating": match.iloc[0]["評分"]
            })
    return matched_bars

# 加載本地數據
combined_bars_path = "D:/YU_LAB_Project_group2/Project-of-group-2/User__Place/combined_bars.csv"
bars_data = load_combined_bars_data(combined_bars_path)

# Dash 應用
app = dash.Dash(__name__)

# 應用佈局
app.layout = html.Div([
    html.H1("台北酒吧推薦系統", style={"text-align": "center"}),

    # 搜尋框
    html.Div([
        html.Label("輸入地點:"),
        dcc.Input(id="location-input", type="text", placeholder="例如: 台北101", style={"width": "80%"}),
        html.Button("搜尋", id="search-button", n_clicks=0)
    ], style={"margin": "20px"}),

    # 地圖視圖
    dcc.Graph(id="map-view"),

    # 推薦酒吧清單
    html.Div(id="recommendation-list", style={"margin": "20px"}),
])

# 定義回調
@app.callback(
    [Output("map-view", "figure"),
     Output("recommendation-list", "children")],
    [Input("search-button", "n_clicks")],
    [Input("location-input", "value")]
)
def update_results(n_clicks, location_input):
    if not location_input:
        return px.scatter_mapbox(), "請輸入地點進行搜尋！"

    # 使用 Geocoding API 獲取地點的緯經度
    geocode_result = gmaps.geocode(location_input)
    if not geocode_result:
        return px.scatter_mapbox(), f"無法找到地點：{location_input}"

    latitude = geocode_result[0]["geometry"]["location"]["lat"]
    longitude = geocode_result[0]["geometry"]["location"]["lng"]

    # 使用 Places API 搜尋酒吧
    places_bars = find_bars_by_keyword(latitude, longitude)
    matched_bars = match_bars(places_bars, bars_data)

    # 更新地圖
    fig = px.scatter_mapbox(
        matched_bars,
        lat="lat",
        lon="lng",
        hover_name="name",
        hover_data=["address", "rating"],
        zoom=14,
        height=500
    )
    fig.update_layout(mapbox_style="open-street-map")

    # 推薦清單
    recommendation_items = [
        html.Li(f"{bar['name']} - 地址: {bar['address']} - 評分: {bar['rating']}")
        for bar in matched_bars
    ]
    return fig, html.Ul(recommendation_items)

# 啟動應用
if __name__ == "__main__":
    app.run_server(debug=True)
