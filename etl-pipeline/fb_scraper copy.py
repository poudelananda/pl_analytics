import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import time
import upload_data

# Set headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MySoccerScraper/1.0)"
}

# Step 1: Scrape the fixture list
fixture_url = "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
res = requests.get(fixture_url, headers=HEADERS)
soup = BeautifulSoup(res.content, "lxml")

# Step 2: Find the fixture table
fixtures_table = soup.find("table", {"id": "sched_2025-2026_9_1"})


# Step 3: Extract match links
matches = []
for row in fixtures_table.find_all("tr"):
    #finding match report link
    match_report_link = row.find("td", {"data-stat": "match_report"})
    gameweek = row.find('th', {'data-stat': 'gameweek'}).text
    if match_report_link and row.find("a", href=True):
        if match_report_link.find("a").text == 'Match Report':
            match_link = match_report_link.find("a")["href"]
            match_id = match_link.split(('/'))[3]
            match_url = "https://fbref.com" + match_link
            #finding the date
            date_cell = row.find("td", {"data-stat": "date"})
            date = date_cell.text.strip() if date_cell else None
            #finding the time
            time_cell = row.find("td", {"data-stat": "start_time"})
            time_val = time_cell.text.strip() if time_cell else None
            #finding home team name link
            home_team_link = row.find("td", {"data-stat": "home_team"})
            home_team_name = home_team_link.text.strip()
            #finding away team name link
            away_team_link = row.find("td", {"data-stat": "away_team"})
            away_team_name = away_team_link.text.strip()
            #finding attendance
            attendance_cell = row.find("td", {"data-stat": "attendance"})
            attendance = attendance_cell.text.strip() if attendance_cell else None
            #finding referee
            referee_cell = row.find("td", {"data-stat": "referee"})
            referee = referee_cell.text.strip() if referee_cell else None

            matches.append((match_url, match_id, date, time_val, home_team_name, away_team_name, attendance, referee, gameweek))

#Step 4: Match team name with corresponding team id:
pl_teams = {"Arsenal":"18bb7c10", "Aston Villa": "8602292d", "Bournemouth": "4ba7cbea", "Brighton": "d07537b9", "Burnley": "943e8050", 
"Brentford": "cd051869", "Chelsea": "cff3d9bb", "Crystal Palace": "47c64c55", "Everton": "d3fd31cc", "Fulham": "fd962109", "Ipswich Town": "b74092de", 
"Leicester City": "a2d435b3", "Leeds United": "5bfb9659", "Liverpool": "822bd0ba", "Manchester City": "b8fd03ef", "Manchester Utd": "19538871", 
"Newcastle Utd": "b2b47a98", "Norwich City": "1c781004", "Nott'ham Forest": "e4a775cb", "Sheffield Utd": "1df6b87e", "Southampton": "33c895d4", 
"Sunderland": "8ef52968", "Tottenham": "361ca564", "Watford": "2abfe087", "West Brom": "60c6b05f", "West Ham":"7c21e445", "Wolves": "8cec06e1"}

# Step 5: Scrape each match report (example: score + xG)
def scrape_match_data(match_url, home_team, away_team):
    print(f"Scraping: {match_url}")
    time.sleep(2)  # Delay between requests
    res = requests.get(match_url, headers=HEADERS)
    soup = BeautifulSoup(res.content, "lxml")
    home_team_id = pl_teams[home_team]
    away_team_id = pl_teams[away_team]

    #Extracting Player IDs for primary key
    home_table = soup.find("table", {"id": f"stats_{home_team_id}_summary"})
    away_table = soup.find("table", {"id": f"stats_{away_team_id}_summary"})
    home_player_ids = [th['data-append-csv'] for th in home_table.find_all('th', attrs={'data-append-csv': True})]
    away_player_ids = [th['data-append-csv'] for th in away_table.find_all('th', attrs={'data-append-csv': True})]
    #Extracting Summary Stats
    home_team_summary = soup.find("table", {"id": f"stats_{home_team_id}_summary"})
    away_team_summary = soup.find("table", {"id": f"stats_{away_team_id}_summary"})
    #Extracting Passing Stats
    home_team_passing = soup.find("table", {"id": f"stats_{home_team_id}_passing"})
    away_team_passing = soup.find("table", {"id": f"stats_{away_team_id}_passing"})
    #Defensive Actions Stats
    home_team_defense = soup.find("table", {"id": f"stats_{home_team_id}_defense"})
    away_team_defense = soup.find("table", {"id": f"stats_{away_team_id}_defense"})
    #Extracting Pass Type Stats
    home_team_passing_types = soup.find("table", {"id": f"stats_{home_team_id}_passing_types"})
    away_team_passing_types = soup.find("table", {"id": f"stats_{away_team_id}_passing_types"})
    #Extracting Possession Stats
    home_team_possession = soup.find("table", {"id": f"stats_{home_team_id}_possession"})
    away_team_possession = soup.find("table", {"id": f"stats_{away_team_id}_possession"})
    #Extracting Miscellaneous Stats
    home_team_misc = soup.find("table", {"id": f"stats_{home_team_id}_misc"})
    away_team_misc = soup.find("table", {"id": f"stats_{away_team_id}_misc"})

    return (home_player_ids, away_player_ids, home_team_summary, away_team_summary, home_team_passing, away_team_passing, home_team_defense, away_team_defense, home_team_passing_types, 
    away_team_passing_types, home_team_possession, away_team_possession, home_team_misc, away_team_misc)
    

#Step 6: Renaming columns for better understanding
def rename_cols(stat_type, df):
    if stat_type == "summary":
        df = df.rename(columns={"Cmp": "Passes_cmp", "Att": "Passes_att", "Cmp%": "Passes_cmp_pct", "Att.1": "Take-ons_att", "Succ":"Take-ons_succ"})
    if stat_type == "passing":
        df = df.rename(columns={"Cmp": "Total_passes_cmp", "Att": "Total_passes_att", "Cmp%": "Total_passes_cmp%", "TotDist": "TotPassDist", "PrgDist": "PrgPassDist",
        "Cmp.1": "Short_passes_cmp", "Att.1": "Short_passes_att", "Cmp%.1": "Short_passes_cmp%", "Cmp.2": "Med_passes_cmp", "Att.2": "Med_passes_att", "Cmp%.2": "Med_passes_cmp%",
        "Cmp.3": "Long_passes_cmp", "Att.3": "Long_passes_att", "Cmp%.3": "Long_passes_cmp%", 'KP': "key_passes", '1/3': "passes_into_final_third", 
        'PPA': "passes_into_pen_area", 'CrsPA':"crosses_into_pen_area" ,'PrgP': "progressive_passes"})
    if stat_type == "passing_types":
        df = df.rename(columns={'Live':"live_ball_passes", 'Dead':"dead_ball_passes", 'FK':'free_kick_passes', 'TB':'through_balls', 'Sw':'switches', 'Crs':'crosses', 
        'TI':'throw_ins', 'CK': 'corner_kicks', 'In': 'inswinging_corner', 'Out': 'outswinging_corner', 'Str': 'straight_corner', 'Cmp': 'passes_completed', 
        'Off': 'passes_offside', 'Blocks': 'passes_blocked'})
    if stat_type == "defense":
        df = df.rename(columns={"Tkl": "Total_tkls", "TklW": "Total_tkls_won", "Tkl.1": "Dribbler_tkls", "Att": "Dribbler_tkls_att", "Tkls%": "Dribbler_tkls%_won", 
        "Lost": "Dribbler_tkls_lost", "Sh": "Shots_blocked", "Pass": "Passes_blocked"})
    if stat_type == "possession":
        df = df.rename(columns={'Touches':"Total_touches",'Def Pen': "Def_pen_touches", 'Def 3rd': "Def_3rd_touches", 'Mid 3rd': "Mid_3rd_touches", 
        'Att 3rd': "Att_3rd_touches", 'Att Pen': "Att_pen_touches", 'Live': "Live_touches", 'Att': "take_ons_att", 'Succ': "take_ons_succ", 'Succ%': "take_ons_succ%",
        'Tkld': "Tkld_during_take_ons", 'Tkld%': "Tkld%_during_take_ons", "Rec": "Passes_received", "PrgR": "Progressive_passes_received"})
    if stat_type == "misc":
        df = df.rename(columns={'CrdY':'yellow_card','CrdR':'red_card', '2CrdY':'two_yellow_cards', 'Fls': 'fouls_committed', 'Fld':'fouls_drawn', 'Off':'offsides', 
        'Crs': 'Crosses', 'TklW': 'Tkls_won','PKcon': "PK_conceded", 'OG': 'own_goals', 'Recov':'ball_recoveries', 'Won': "Aerial_Duels_won", 'Lost': "Aerial_Duels_lost", 
        'Won%': "Aerial_Duels_won%"})
    return df
    
# Step 7: Loop and store all match data
for url, match_id, date, time_val, home_team, away_team, attendance, referee, gameweek in matches:  # Limit to 10 to test
    game_data = scrape_match_data(url, home_team, away_team)
    stat_type = ["player_ids", "summary", "passing", "defense", "passing_types", "possession", "misc"]
    home_player_ids = []
    away_player_ids = []
    for stat in stat_type:
        stat_dict = {"player_ids": [0,1], "summary": [2,3], "passing":[4,5], "defense":[6,7], "passing_types":[8,9], "possession":[10,11], "misc": [12, 13]}
        #dataset type
        home_stats = game_data[stat_dict[stat][0]]
        away_stats = game_data[stat_dict[stat][1]]

        #When reading as html, it comes as a list as it assumes we are reading in multiple tables and we only need the first item on the list.
        if stat == "player_ids":
            home_player_ids = home_stats
            away_player_ids = away_stats
        else:
            home_df = pd.read_html(str(home_stats), header = 1)[0]
            away_df = pd.read_html(str(away_stats), header = 1)[0]
            home_df['game_date'] = date
            away_df['game_date'] = date
            home_df['time'] = time_val
            away_df['time'] = time_val
            home_df['match_id'] = match_id
            away_df['match_id'] = match_id
            home_df['attendance'] = attendance
            away_df['attendance'] = attendance
            home_df['referee'] = referee
            away_df['referee'] = referee
            home_df['gameweek'] = gameweek
            away_df['gameweek'] = gameweek
            home_df['team'] = home_team
            away_df['opponent'] = away_team
            home_df['opponent'] = away_team
            away_df['opponent'] = home_team
            home_df['location'] = "home"
            away_df['location'] = "away"
            #removing the total count that appears at the bottom
            home_df = home_df[:len(home_df)-1]
            away_df = away_df[:len(away_df)-1]
            home_df['player_id'] = home_player_ids
            away_df['player_id'] = away_player_ids
            final_df = pd.concat([home_df, away_df], ignore_index=True)
            final_df = rename_cols(stat, final_df)
            upload_data.upload_data(final_df, stat)
            final_df.to_csv(f'{stat}.csv', index = False)
        