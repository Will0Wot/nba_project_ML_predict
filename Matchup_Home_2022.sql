SELECT
    game_id,
    game_date,
    season_id,
    team_id_home AS team_id,
    team_name_home AS team_name,
    'home' AS location,
    fgm_home AS fgm,
    fga_home AS fga,
    fg3m_home AS fg3m,
    fg3a_home AS fg3a,
    ftm_home AS ftm,
    fta_home AS fta,
    oreb_home AS oreb,
    dreb_home AS dreb,
    reb_home AS reb,
    ast_home AS ast,
    stl_home AS stl,
    blk_home AS blk,
    tov_home AS tov,
    pf_home AS pf,
    pts_home AS pts,
    plus_minus_home AS plus_minus,
    wl_home AS result
FROM game
WHERE season_id = '22022'

UNION ALL

SELECT
    game_id,
    game_date,
    season_id,
    team_id_away AS team_id,
    team_name_away AS team_name,
    'away' AS location,
    fgm_away AS fgm,
    fga_away AS fga,
    fg3m_away AS fg3m,
    fg3a_away AS fg3a,
    ftm_away AS ftm,
    fta_away AS fta,
    oreb_away AS oreb,
    dreb_away AS dreb,
    reb_away AS reb,
    ast_away AS ast,
    stl_away AS stl,
    blk_away AS blk,
    tov_away AS tov,
    pf_away AS pf,
    pts_away AS pts,
    plus_minus_away AS plus_minus,
    wl_away AS result
FROM game
WHERE season_id = '22022';