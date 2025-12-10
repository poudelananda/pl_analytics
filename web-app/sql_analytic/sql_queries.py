import sqlite3
import pandas as pd
from collections import Counter

db_path = "/Users/m33210/Desktop/Anandas Documents/AP Projects/soccer_analytics/pl_database.db"

#Getting player stats
def get_player_stats(player_name):
    query = """
        SELECT a.Player, a.Team, a.Opponent, a.Gls, a.Sh, a.SoT, b.Date
        FROM summary a
        JOIN fixtures b ON a.match_id = b.match_id
        WHERE a.Player = ?
        ORDER BY b.Date
    """
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn, params=[player_name])

    df["Sh"] = pd.to_numeric(df["Sh"], errors="coerce")
    df = df.dropna(subset=["Sh"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    return df


#Setting primary positions based on the most frequent number of positions played by a player 
def get_primary_positions():

    query = "SELECT Player, Pos FROM summary"
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)

    def determine_primary_position(pos_series):
        all_positions = []
        for pos in pos_series:
            if pd.isna(pos):
                continue
            parts = [p.strip() for p in str(pos).split(",")]
            all_positions.extend(parts)

        if not all_positions:
            return None

        return Counter(all_positions).most_common(1)[0][0]

    primary_pos_df = (
        df.groupby("Player")["Pos"]
        .apply(determine_primary_position)
        .reset_index()
        .rename(columns={"Pos": "PrimaryPos"})
    )

    return primary_pos_df

def overall_team_stats():
    query = """
        select a.Team, a.Opponent, a.Sh, a.SoT
        from summary a
    """
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn)

    df["Sh"] = pd.to_numeric(df["Sh"], errors="coerce")
    df = df.dropna(subset=["Sh"])

    total_shots_for_df = (
        df.groupby(["opponent"])["Sh"]
        .agg(["mean", "sum"])
        .reset_index()
        .rename(columns={
            "mean": "avg_shots",
            "sum": "total_shots"
        })
    )
    avg_shots_for_df = (
        df.groupby(["opponent", "team"])["Sh"]
        .agg(["mean", "sum"])
        .reset_index()
        .rename(columns={
            "mean": "avg_shots",
            "sum": "total_shots"
        })
    )

    total_shots_against_df = (
        df.groupby(["team"])["Sh"]
        .agg(["mean", "sum"])
        .reset_index()
        .rename(columns={
            "mean": "avg_shots",
            "sum": "total_shots"
        })
    )
    avg_shots_against_df = (
        df.groupby(["team", "opponent"])["Sh"]
        .agg(["mean", "sum"])
        .reset_index()
        .rename(columns={
            "mean": "avg_shots",
            "sum": "total_shots"
        })
    )

    return shots_for_df, shots_against_df



def get_team_stats(team_name):
    query = """
        SELECT a.Player, a.Team, a.Opponent, a.Pos, a.Gls, a.Sh, a.SoT, b.Date
        FROM summary a
        JOIN fixtures b ON a.match_id = b.match_id
        WHERE a.Team = ? or a.Opponent = ?
        ORDER BY b.Date
    """

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(query, conn, params=[team_name,team_name])

    df["Sh"] = pd.to_numeric(df["Sh"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Sh", "Date"])

    primary_positions = get_primary_positions()
    df = df.merge(primary_positions, on="Player", how="left")
    df = df.drop_duplicates(subset = ['Player', 'team', 'opponent', 'Date'])
    
    df_shots_for = df[df['team'] == team_name]
    df_shots_against = df[df['opponent'] == team_name]

    shots_for_df = (
        df_shots_for.groupby(["opponent", "Date"])["Sh"]
        .sum()
        .reset_index()
        .rename(columns={"Sh": "total_shots"})
    )

    position_shots_for_df = (
        df_shots_for.groupby("PrimaryPos")["Sh"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={
            "mean": "avg_shots",
            "std": "std_dev_shots",
            "count": "num_matches"
        })
    )

    conceded_df = (
        df_shots_against.groupby(["team","Date"])["Sh"]
        .sum()
        .reset_index()
        .rename(columns={"Sh": "total_shots"})
    )

    position_conceded_df = (
        df_shots_against.groupby("PrimaryPos")["Sh"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={
            "mean": "avg_shots",
            "std": "std_dev_shots",
            "count": "num_matches"
        })
    )


    return shots_for_df, position_shots_for_df, conceded_df, position_conceded_df
