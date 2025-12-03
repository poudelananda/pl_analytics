import psycopg2
import pandas as pd

# Load CSV
df = pd.read_csv("summary.csv")
aws_password = pd.read_csv("/Users/m33210/Desktop/Ananda's Documents/AP Projects/soccer_analytics/aws_password.csv")['password'][0]

conn = psycopg2.connect(
    host='pl-stats.c5sygygwsbg0.us-east-2.rds.amazonaws.com',
    database='postgres',
    user='postgres',
    password=aws_password,
    port='5432'
)

cur = conn.cursor()

# column_exist_query = '''select count(*) as column_count from information_schema.columns where table_schema = 'public' and table_name = 'summary';'''
# columns = ", ".join(
#     [f'"{col}" TEXT' for col in df.columns]  # Default all to TEXT; you can customize types
# )

# cur.execute(column_exist_query)
# table_cnt = cur.fetchone()[0]
# print(table_cnt)
# print(len(df.columns))
# select_qry = "select column_name, data_type from information_schema.columns where table_schema = 'public' and table_name = 'summary';"
# cur.execute(select_qry)
# print(cur.fetchall())
# qry_cols = cur.fetchall()
# qry_cols_list =  []
# for col in qry_cols:
#     qry_cols_list.append(col[0])
# #Need to check two things: 1)if the columns from the dataframe are in the database. 2) if the columns from the database are in the dataframe.
# for col in df.columns:
#     if col not in qry_cols_list:
#         print(f"{col} column is not in the database")
# for col in qry_cols_list:
#     if col not in df.columns:
#         print(f"{col} column is not in the dataframe")


#Looking at distinct match ids
# select_qry = f"select distinct match_id from summary;"
# cur.execute(select_qry)
# match_id = cur.fetchall()
# match_id_list = []
# for game in match_id:
#     match_id_list.append(game[0])

#DELETION
# stat_type = ["summary", "passing", "defense", "passing_types", "possession", "misc"]
# for stat in stat_type:
#     delete_qry =  f"drop table if exists {stat}"
#     cur.execute(delete_qry)
#     conn.commit()


