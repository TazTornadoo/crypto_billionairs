from data_storage import create_connection
import pandas as pd
import numpy as np
from stockstats import StockDataFrame


def momentum(df, lag):
    return df.pct_change(periods=lag)

def create_buy_signals():
    
    connection = create_connection("../database/crypto_billionairs.db")
    df = pd.read_csv('../database/ETH_1min.txt', sep=",")
    df.columns = ["time", "open", "high", "low", "close", "volume"]
    df["return"] = df['close'].pct_change() + 1
    
    df_ti = pd.DataFrame()
    df_ti["open_time"] = df["time"]
    df_ti["open"] = df["open"]
    df_ti["close"] = df["close"]
    df_ti["high"] = df["high"]
    df_ti["low"] = df["low"]
    df_ti["volume"] = df["volume"]
    stock = StockDataFrame.retype(df_ti)
    
    df["stochastic_oscillator"] = stock.get("kdjk")
    df["relative_strength_index"] = stock.get("rsi_30")
    
    df["buy_indicator"] = 0
    df.loc[df["relative_strength_index"] < 20, 'buy_indicator'] = 1
    
    df["close_indicator"] = 0
    df.loc[df["relative_strength_index"].shift(2016) < 20, 'close_indicator'] = 1
    
    df.to_sql("ETHUSDT_1m_complete_history_long", connection, if_exists="replace")
    

def create_sell_signals():
    df = pd.read_csv('../database/ETH_1min.txt', sep=",")
    connection = create_connection("../database/crypto_billionairs.db")
    
    df.columns = ["time", "open", "high", "low", "close", "volume"]
    df["return"] = df['close'].pct_change() + 1
    
    df_ti = pd.DataFrame()
    df_ti["open_time"] = df["time"]
    df_ti["open"] = df["open"]
    df_ti["close"] = df["close"]
    df_ti["high"] = df["high"]
    df_ti["low"] = df["low"]
    df_ti["volume"] = df["volume"]
    
    stock = StockDataFrame.retype(df_ti)
    
    df["moving_average_convergence_divergence"] = stock.get("macd")
    df["moving_average_convergence_divergence"] = df["moving_average_convergence_divergence"].astype(int)
    
    short_signals1 = df.index[(df["moving_average_convergence_divergence"] >= 40) & (df["moving_average_convergence_divergence"] <= -70)].tolist()
    short_signals = short_signals1
    
    df["short_indicator"] = 0
    df["short_indicator"].loc[short_signals] = 1
    
    df["short_close_indicator"] = 0
    df["short_close_indicator"] = df["short_indicator"].shift(2016)
    
    df.to_sql("ETHUSDT_1m_complete_history_short", connection, if_exists="replace")
    

def create_daily_adjustment():
    df = pd.read_csv('../database/ETH_1min.txt', sep=",")
    connection = create_connection("../database/crypto_billionairs.db")
    
    df["momentum_day"] = momentum(df["close"], 1440)
    
    df["buy_indicator"] = 0
    df.loc[df["momentum_day"] > 0, 'buy_indicator'] = 1
    df.loc[df["momentum_day"] < 0, 'short_indicator'] = -1
    
    df.to_sql("ETHUSDT_1m_complete_history_short", connection, if_exists="replace")
    
    
create_daily_adjustment()