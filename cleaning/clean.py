import pandas as pd

df = pd.read_csv('root/csv/2022_merge.csv')

# Advanced metrics
df['possessions'] = df['fga'] + 0.44 * df['fta'] - df['oreb'] + df['tov']
df['true_shooting'] = df['pts'] / (2 * (df['fga'] + 0.44 * df['fta']))
df['off_rtg'] = 100 * df['pts'] / df['possessions']
df['turnover_pct'] = df['tov'] / (df['fga'] + 0.44 * df['fta'] + df['tov'])
df['pace'] = df['possessions']  # Approximation
df['def_rtg'] = None  
df['rebound_pct'] = None  
df['location_home'] = (df['location'] == 'home').astype(int)

# Add game_id and team_id to selected features
selected_columns = [
    'game_id', 'team_id', 'team_name', 'location_home', 'pts', 'ast', 'fgm', 'fga',
    'fg3m', 'fg3a', 'fta', 'oreb', 'dreb', 'reb',
    'possessions', 'true_shooting', 'off_rtg', 'turnover_pct', 'pace',
    'rebound_pct', 'def_rtg', 'result'
]

df = df[selected_columns]

df.to_csv('root/csv/2022_features.csv', index=False)