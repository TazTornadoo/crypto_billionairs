import wget
from datetime import date, datetime, timedelta
import os
import pandas as pd
from data_storage import connection
import time

def download_binance_data(price_type, granularity, trading_pair, time_interval, history_days, path, db_connection):
    #to make this function more efficient we should check if a table with this data already exist

    for history_day in range(1, history_days + 1):

        time.sleep(5)

        today = datetime.today() - timedelta(days=history_day)
        date_ = today.strftime("%Y-%m-%d")
        data_file = f"{trading_pair}-{time_interval}-{date_}"


        url = f"https://data.binance.vision/data/{price_type}/{granularity}/klines/{trading_pair}/{time_interval}/{data_file}.zip"

        db_cursor = db_connection.cursor()

        db_cursor.execute(f"SELECT 1 FROM sqlite_master WHERE type='table' AND name='{data_file}';")
            
        is_table_there = db_cursor.fetchall()

        if is_table_there != [(1, )]:
            wget.download(url, out=path)

  
def load_data_to_database(path, db_connection, header_list):

    
    for file in os.listdir(path):
        df = pd.read_csv(f'{path}/{file}', names = header_list)

        if file[-3:] == 'zip':
            df.to_sql(f'{file[:-4]}', con=db_connection, if_exists="replace", index=False)
            os.remove(f'{path}/{file}')


download_binance_data("spot", "daily", "ETHTUSD", "3m", 4, "Data/raw_data", connection)

header = ['open time', 'open',
          'high', 'low', 'close',
          'volume', 'close_time', 
          'quote_asset_volume', 'number_of_trades',
          'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']


load_data_to_database('Data/raw_data', connection, header)