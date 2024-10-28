from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd

# 獲取 LeBron James 的球員 ID
lebron = next((player for player in players.get_players() if player['full_name'] == "LeBron James"), None)

if lebron:
    season = "2023-24"  # 2024 賽季的格式
    game_log = playergamelog.PlayerGameLog(player_id=lebron['id'], season=season)
    lebron_data = game_log.get_data_frames()[0]
    print(lebron_data)
else:
    print("在球員資料庫中找不到 LeBron James。")
