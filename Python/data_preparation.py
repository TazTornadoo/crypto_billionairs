import pandas as pd
import numpy as np
from data_storage import connection
from risk_metrics import Risk_Metrics
import os


headers = ["time", "open", "high", "low", "close", "volume"]

def prepare_files(path, db_connection, header_list):
    
    for file in os.listdir(path):
        try:
            if file[-3:] == 'txt':
                df = pd.read_csv(f'./{path}/{file}', names = header_list, sep =",")
            
                
                df["momentum_1day"] = momentum(df["close"], 10080)
    
                df["buy_indicator"] = 0
                df.loc[df["momentum_1week"] > 0.025, 'buy_indicator'] = 1
                df.loc[df["momentum_1week"] < -0.08, 'short_indicator'] = -1
        

            
                file_name = str(file).replace("-", "_") + '_complete_history_long_short'
                df.to_sql(f'{file_name[:-4]}', con=db_connection, if_exists="replace", index=False)
                #os.remove(f'{path}/{file}')
        except:
            pass
        
def momentum(df, lag):
    return df.pct_change(periods=lag)

def init_buy_signal(df):
    
    return df['buy_indicator']

def init_short_signal(df):
    
    return df['short_indicator']

class Momentum_1m_long_short(Strategy):
   
    
    def init(self):
        # compute the rsi and stochastic oscillator with stockstats and return the buy signal of the current row
        
        self.buy_init = self.I(init_buy_signal, self.data.df)
        self.short_init = self.I(init_short_signal, self.data.df)
        self.data.df.drop(self.data.df.columns.difference(['Open', 'High', 'Low', 'Close', "Volume"]), 1, inplace=True)
        
       
    
    def next(self):
        
        if self.buy_init[-1] == 1 and self.position.is_long is False:
            self.position.close()
            self.buy()

             
        elif self.short_init[-1] == -1 and self.position.is_short is False:
            self.position.close()
            self.sell()
            
    
def run_backtesting(db_connection):
    
    table_names = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;", db_connection)

    table_names_list = table_names['name'].tolist()

    filtered_table_names = [name for name in table_names_list if "1m_complete_history_long_short" in name ]
    
    df_risk = pd.DataFrame()
    df_risk.columns = ["table_name", "return", "annualized_return", "sharpe_ratio_annualized", "sortino_ratio_annualized", "maximum_drawdown", "calamr_ratio_annualized"]
    
    for table in filtered_table_names:
        
        df = pd.read_sql_query(f"table", db_connection)
        
        bt = Backtest(df, Momentum_1m_long_short, cash=10_000, commission=.001)
        stats = bt.run()
        trades = pd.DataFrame(stats['_trades'])
        trades.to_sql(f"trades_{table}", db_connection, if_exists="replace")
        
        risk = Risk_Metrics(trades, df, 0)
        risk_metrics_list = [f"{table}", stats["Return [%]"], risk._annualize(stats["Return [%]"], df),
                             risk.sharpe_ratio("momentum_1week"), risk.sortino_ratio("momentum_1week"),
                             risk.max_drawdown(), risk.calmar_ratio()]
        df_risk.append()
    
    df_risk.to_sql("cryptocurrencies_risk_metrics_1m", db_connection, if_exists="replace")
        
        
        
prepare_files("database", connection, headers)

run_backtesting(connection)
