SELECT  
    team_name_home AS team_home,
    wl_home AS win_loss,
	matchup_home AS matchup
FROM game
WHERE season_id = '22022';