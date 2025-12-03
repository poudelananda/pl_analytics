import psycopg2
import pandas as pd
import sqlite3

# Load CSV
##Iterate through all the datasets
#df = pd.read_csv("summary.csv")

def upload_fixtures(df):
    conn = sqlite3.connect("/Users/m33210/Desktop/Anandas Documents/AP Projects/soccer_analytics/pl_database.db")
    cur = conn.cursor()
    table_name = "fixtures"
    columns = ", ".join(
        [f'"{col}" TEXT' for col in df.columns]  # Default all to TEXT; you can customize types
    )
    create_table_sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns});'
    cur.execute(create_table_sql)
    conn.commit()
    for row in df.itertuples(index=False):
        values = tuple(row)
        placeholders = ', '.join(['?'] * len(values))
        insert_sql = f'INSERT INTO {table_name} VALUES ({placeholders})'
        cur.execute(insert_sql, values)
        conn.commit()
        print(f"{row} inserted into {table_name}")
    cur.close()
    conn.close()
    

def upload_data(df, stat_type):
    conn = sqlite3.connect("/Users/m33210/Desktop/Anandas Documents/AP Projects/soccer_analytics/pl_database.db")
    cur = conn.cursor()
    # Dynamically build CREATE TABLE statement
    table_name = stat_type
    columns = ", ".join(
        [f'"{col}" TEXT' for col in df.columns]  # Default all to TEXT; you can customize types
    )
    create_table_sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns});'

    cur.execute(create_table_sql)
    conn.commit()
    

    #Checking to see if all the columns exist in the database and vice versa.
    # select_qry = f"select column_name from information_schema.columns where table_schema = 'public' and table_name = '{table_name}';" #postgres version
    select_qry = f"PRAGMA table_info({table_name});" #sqlite version
    cur.execute(select_qry)
    qry_cols = cur.fetchall()
    qry_cols_list = []
    error_count = 0
    for col in qry_cols:
        qry_cols_list.append(col[1])
    for col in df.columns:
        if col not in qry_cols_list:
            print(f"{col} column is not in the {table_name} sql table")
            error_count += 1
    for col in qry_cols_list:
        if col not in df.columns:
            print(f"{col} column is not in the {table_name} dataframe")
            error_count += 1
    if error_count == 0:
        #Check whether the table you're about to insert is already there based on the match id and game year (just in case the match id repeats later)
        game_id_query = f"select distinct match_id from {table_name};"
        cur.execute(game_id_query)
        match_id = cur.fetchall()
        if len(match_id) == 0:
            for row in df.itertuples(index=False):
                values = tuple(row)
                placeholders = ', '.join(['?'] * len(values))
                insert_sql = f'INSERT INTO {table_name} VALUES ({placeholders})'
                cur.execute(insert_sql, values)
                conn.commit()
            print(f"Table `{table_name}` created and data inserted.")
                
        else:
            match_id_list = []
            for game in match_id:
                match_id_list.append(game[0])
            df_match_id = str(df['match_id'].unique()[0])
            if df_match_id not in match_id_list:
                for row in df.itertuples(index=False):
                    values = tuple(row)
                    placeholders = ', '.join(['?'] * len(values))
                    insert_sql = f'INSERT INTO {table_name} VALUES ({placeholders})'
                    cur.execute(insert_sql, values)
                    conn.commit()

                print(f"Table `{table_name}` created and data inserted for match {df_match_id}")
            else:
                print(f"Match ID {df_match_id} already exists in the database for {table_name}.")
    else:
        print("No data was uploaded.")

    cur.close()
    conn.close()

