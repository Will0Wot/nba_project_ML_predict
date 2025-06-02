import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import time
import os

# Create directories
os.makedirs('root/csv/player_logs', exist_ok=True)

# Load all active players
all_players = pd.DataFrame(players.get_active_players())

# Initialize a DataFrame to collect all logs
all_logs = []

# Loop through each player and fetch logs
for i, player in all_players.iterrows():
    player_id = player['id']
    player_name = player['full_name']
    file_path = f'root/csv/player_logs/{player_id}.csv'
    if os.path.exists(file_path):
        print(f"📁 Skipping {player_name}, logs already exist.")
        df = pd.read_csv(file_path)
        all_logs.append(df)
        continue
    print(f"Fetching logs for {player_name}...")
    try:
        logs = playergamelog.PlayerGameLog(player_id=player_id, season='2022-23')
        df = logs.get_data_frames()[0]
        df['PLAYER_NAME'] = player_name
        df.to_csv(file_path, index=False)
        all_logs.append(df)
        time.sleep(0.6)  # Rate limit to avoid getting blocked
    except Exception as e:
        print(f"❌ Failed for {player_name}: {e}")

