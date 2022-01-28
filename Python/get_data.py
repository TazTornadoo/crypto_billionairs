from mimetypes import encodings_map
import wget
from datetime import date, datetime, timedelta
import os
import pandas as pd
from data_storage import connection
import time


#maybe write as a class with trading_pair and db connection as initialisation parameters
def download_binance_data(price_type, granularity, trading_pair, time_interval, history_days, path, db_connection):
    #to make this function more efficient we should check if a table with this data already exist

    for history_day in range(1, history_days + 1):

        today = datetime.today() - timedelta(days=history_day)
        date_ = today.strftime("%Y-%m-%d")
        data_file = f"{trading_pair}-{time_interval}-{date_}"


        url = f"https://data.binance.vision/data/{price_type}/{granularity}/klines/{trading_pair}/{time_interval}/{data_file}.zip"

        db_cursor = db_connection.cursor()

        file_name = str(data_file).replace("-", "_")

        db_cursor.execute(f"SELECT 1 FROM sqlite_master WHERE type='table' AND name='{file_name}';")
            
        is_table_there = db_cursor.fetchall()

        if is_table_there != [(1, )]:
            try:
                wget.download(url, out=path)
            
            except:
                return

  
def load_data_to_database(path, db_connection, header_list):

    
    for file in os.listdir(path):
        try:
            df = pd.read_csv(f'./{path}/{file}', names = header_list)
        

            if file[-3:] == 'zip':
                file_name = str(file).replace("-", "_")
                df.to_sql(f'{file_name[:-4]}', con=db_connection, if_exists="replace", index=False)
                os.remove(f'{path}/{file}')
        except:
            pass


def union_tables(trading_pair, db_connection):

    table_names = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;", db_connection)

    table_names_list = table_names['name'].tolist()

    filtered_table_names = [name for name in table_names_list if trading_pair in name and 'history' not in name]

    union_all_sql_list = []

#Rewrite as list comprehension
    for name in filtered_table_names[:-1]:
        if trading_pair in name and 'history' not in name:
            union_new_table = f'SELECT * FROM {name} UNION ALL'
            union_all_sql_list.append(union_new_table)
    
    union_all_sql_list.append(f'SELECT * from {filtered_table_names[-1]}')

    union_all_sql = ' '.join(union_all_sql_list)

#Potentially ineffiecent, might be worth trying to use only SQL and not loading into a dataframe first
    df = pd.read_sql_query(union_all_sql, db_connection)

    df.to_sql(f'{trading_pair}_complete_history', con=db_connection, if_exists="replace", index=False)


download_binance_data("spot", "daily", "ETHTUSD", "3m", 360, "Data/raw_data", connection)

header = ['open time', 'open',
          'high', 'low', 'close',
          'volume', 'close_time', 
          'quote_asset_volume', 'number_of_trades',
          'taker_buy_base_asset_volume',
          'taker_buy_quote_asset_volume', 'ignore']


load_data_to_database('Data/raw_data', connection, header)

union_tables('ETHTUSD', connection)
