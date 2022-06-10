import pandas as pd
import numpy as np
import statistics


class Risk_Metrics():

    def __init__(self, trades, ohlcv_data, risk_free_return, daily_granularity, stats):
        self.trades = trades 
        self.ohlcv_data = ohlcv_data
        self.risk_free_return = risk_free_return
        self.daily_granularity = daily_granularity
        self.stats = stats
    
    def _annualize(self, trade_return):
        
        if self.daily_granularity == False:
            annualized_return = trade_return ** 1/ (len(self.ohlcv_data) / (24 * 60 *365))
        
        else:
            annualized_return = trade_return
        
        return annualized_return 
    
    
    def sharpe_ratio(self, column_name):
        
        portfolio_returns = []
        
    
        for index, row in self.trades[['EntryBar', 'ExitBar', 'Size']].iterrows():
        
            if row['Size'] > 0:
                portfolio_returns.extend(self.ohlcv_data[column_name][row['EntryBar']:row['ExitBar']].to_list())
                
            
            else:
                temporary = self.ohlcv_data[column_name][row['EntryBar']:row['ExitBar']].to_list()
                short_returns = [x for x in temporary]#[2 - x for x in temporary]

                portfolio_returns.extend(short_returns)
        
        if self.daily_granularity == True:
            portfolio_returns = self.trades["ReturnPct"] + 1
        
        portfolio_returns = [x for x in portfolio_returns if isinstance(x, str) != True]

        s = statistics.stdev(portfolio_returns)
        
        annual_return = self._annualize(self.stats["Return [%]"] / 100)
        
        sharpe_ratio = (annual_return - self.risk_free_return) / s

        return sharpe_ratio
    
    
    
    def sortino_ratio(self, column_name):
        
        portfolio_returns = []
    
        for index, row in self.trades[['EntryBar', 'ExitBar', 'Size']].iterrows():
            
            if row['Size'] > 0:
                portfolio_returns.extend(self.ohlcv_data[column_name][row['EntryBar']:row['ExitBar']].to_list())
            
            else:
                temporary = self.ohlcv_data[column_name][row['EntryBar']:row['ExitBar']].to_list()
                short_returns = [x for x in temporary]

                portfolio_returns.extend(short_returns) 
                
        if self.daily_granularity == True:
            portfolio_returns = self.trades["ReturnPct"] + 1
            
        
        downside_portfolio_returns = [x if x < 1 else 0 for x in portfolio_returns]
        # Calculate Standard Deviation

        s = statistics.stdev(downside_portfolio_returns)
        
        annual_return = self._annualize(self.stats["Return [%]"] / 100)
        
        sortino_ratio = (annual_return - self.risk_free_return) / s
        
        return sortino_ratio
    
    
    def max_drawdown(self):
        
        portfolio_return = np.cumprod(self.trades["ReturnPct"] + 1)
        
        peak, peak_index = portfolio_return.max(), portfolio_return.argmax()
        
        low = portfolio_return[peak_index:].min()
        
        max_drawdown = (peak - low)/peak
        
        return max_drawdown
    
    def calmar_ratio(self, trade_return):
        
        annual_return = self._annualize(self.stats["Return [%]"] / 100)
        
        if self.max_drawdown() > 0:
            calmar_ratio_ = (annual_return - self.risk_free_return) / self.max_drawdown()

            return calmar_ratio_
        
        return 0