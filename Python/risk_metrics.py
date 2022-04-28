import pandas as pd
import numpy as np


class Risk_Metrics():

    def __init__(self, trades, ohlcv_data, risk_free_return):
        self.trades = trades 
        self.ohlcv_data = ohlcv_data
        self.risk_free_return = risk_free_return
    
    
    def _std_dev(price_timeseries):
        
        n = len(price_timeseries)
        
        mean = sum(price_timeseries) / n
        
        deviations = sum([(x - mean)**2 for x in price_timeseries])
        variance = deviations / (n - 1)
        standard_deviation = variance**(1/2)
        
        return standard_deviation
    
    
    def _annualize(self, trade_return):
        
        annualized_return = trade_return ** 1/ (len(self.ohlcv_data) / (24 * 60 * 365))
        
        return annualized_return 
    
    
    def sharpe_ratio(self, column_name):
        
        portfolio_returns = []
        
    
        for index, row in self.trades[['EntryBar', 'ExitBar', 'Size']].iterrows():
        
            if row['Size'] > 0:
                portfolio_returns.extend(self.ohlcv_data[column_name][row['EntryBar']:row['ExitBar']].to_list())
                
            
            else:
                temporary = self.ohlcv_data[column_name][row['EntryBar']:row['ExitBar']].to_list()
                short_returns = [2 - x for x in temporary]

                portfolio_returns.extend(short_returns) 
    
        s = Risk_Metrics._std_dev(portfolio_returns)
    
        portfolio_return = np.cumprod(self.trades["ReturnPct"] + 1)
        
        annual_return = self._annualize(portfolio_return[-1:].item())

        sharpe_ratio = (annual_return - self.risk_free_return) / s

        return sharpe_ratio
    
    
    
    def sortino_ratio(self, column_name):
        
        portfolio_returns = []
    
        for index, row in self.trades[['EntryBar', 'ExitBar', 'Size']].iterrows():
            
            if row['Size'] > 0:
                portfolio_returns.extend(self.ohlcv_data[column_name][row['EntryBar']:row['ExitBar']].to_list())
            
            else:
                temporary = self.ohlcv_data[column_name][row['EntryBar']:row['ExitBar']].to_list()
                short_returns = [2 - x for x in temporary]

                portfolio_returns.extend(short_returns) 
        
        downside_portfolio_returns = [x for x in portfolio_returns if x < 1]
        # Calculate Standard Deviation
        s = Risk_Metrics._std_dev(downside_portfolio_returns)
        portfolio_return = np.cumprod(self.trades["ReturnPct"] + 1)
        
        annual_return = self._annualize(portfolio_return[-1:].item())
        
        sortino_ratio = (annual_return - self.risk_free_return) / s
        
        return sortino_ratio
    
    
    def max_drawdown(self):
        
        portfolio_return = np.cumprod(self.trades["ReturnPct"] + 1)
        
        peak, peak_index = portfolio_return.max(), portfolio_return.argmax()
        
        low = portfolio_return[peak_index:].min()
        
        max_drawdown = (peak - low)/peak
        
        return max_drawdown
    
    def calmar_ratio(self, trade_return):
        
        annual_return = self._annualize(trade_return)
        if self.max_drawdown() > 0:
            calmar_ratio = (annual_return - self.risk_free_return) / self.max_drawdown()

        return calmar_ratio