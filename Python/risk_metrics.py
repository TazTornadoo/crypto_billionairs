import pandas as pd
import numpy as np
import statistics


class Risk_Metrics():

    def __init__(self, trades, ohlcv_data, risk_free_return, stats):
        self.trades = trades 
        self.ohlcv_data = ohlcv_data
        self.risk_free_return = risk_free_return
        self.stats = stats
        
    
    def sharpe_ratio(self, column_name):
        
        
        portfolio_returns = self.trades["ReturnPct"] + 1
        
        portfolio_returns = [x for x in portfolio_returns if isinstance(x, str) != True]

        s = statistics.stdev(portfolio_returns)
        
        sharpe_ratio = (self.stats["Return [%]"] / 100 - self.risk_free_return) / s

        return sharpe_ratio
    
    
    
    def sortino_ratio(self, column_name):
        
        
        portfolio_returns = self.trades["ReturnPct"] + 1

        downside_portfolio_returns = [x if x < 1 else 0 for x in portfolio_returns]
        
        if len(downside_portfolio_returns) == 0:
            return 0
        
        # Calculate Standard Deviation
        s = statistics.stdev(downside_portfolio_returns)
        
        if s == 0:
            return 0
        
        sortino_ratio = (self.stats["Return [%]"] / 100 - self.risk_free_return) / s
        
        return sortino_ratio
    
    
    def max_drawdown(self):
        
        portfolio_return = np.cumprod(self.trades["ReturnPct"] + 1)
        
        peak, peak_index = portfolio_return.max(), portfolio_return.argmax()
        
        low = portfolio_return[peak_index:].min()
        
        max_drawdown = (peak - low)/peak
        
        return max_drawdown
    
    def calmar_ratio(self):
        
        if self.max_drawdown() > 0:
            calmar_ratio_ = (self.stats["Return [%]"] / 100 - self.risk_free_return) / self.max_drawdown()

            return calmar_ratio_
        
        return 0