import pandas as pd
import numpy as np
import statistics


class Risk_Metrics():
    
    #the class requires the trades of the backtest, the market data of the backtest,
    #the risk free return rate and lastly a stats object which is created by a backtest

    def __init__(self, trades, ohlcv_data, risk_free_return, stats):
        self.trades = trades 
        self.ohlcv_data = ohlcv_data
        self.risk_free_return = risk_free_return
        self.stats = stats
        self.equity_curve = stats["_equity_curve"].reset_index()
        
    
    def _annualize(self, total_return):
        
        # annualizes the total return of the backtest
        if total_return < 0:
            total_return = total_return * -1
            annualized_return = total_return ** (1 / (len(self.ohlcv_data) / 365 ))
            
            annualized_return = annualized_return * -1
            
        else:
            annualized_return = total_return ** (1 / (len(self.ohlcv_data) / 365 ))
        
        return annualized_return 
    
    def sharpe_ratio(self):
        #returns the sharpe ratio of the backtest
        
        portfolio_returns = self.trades["ReturnPct"] + 1
        
        portfolio_returns = [x for x in portfolio_returns if isinstance(x, str) != True]
        
        if len(portfolio_returns) == 0:
            return 0

        s = statistics.stdev(portfolio_returns)
        
        annualized_return = self._annualize(self.stats["Return [%]"] / 100)
        
        sharpe_ratio = (annualized_return - self.risk_free_return) / s

        return sharpe_ratio
    
    
    
    def sortino_ratio(self):
        #returns the sortino ratio of the backtest
        
        portfolio_returns = self.trades["ReturnPct"] + 1

        downside_portfolio_returns = [x if x < 1 else 0 for x in portfolio_returns]
        
        if len(downside_portfolio_returns) == 0:
            return 0
        
        # Calculate Standard Deviation
        s = statistics.stdev(downside_portfolio_returns)
        
        if s == 0:
            return 0
        
        annualized_return = self._annualize(self.stats["Return [%]"] / 100)
        
        sortino_ratio = (annualized_return - self.risk_free_return) / s
        
        return sortino_ratio
    
    
    def max_drawdown(self):
        #returns the maximum drawdown of the backtest
        
        peak = self.equity_curve["Equity"].max()
        peak_index = self.equity_curve["Equity"].idxmax()
        low = self.equity_curve["Equity"].iloc[peak_index:].min()

        max_drawdown = (low - peak)/peak
        
        return max_drawdown
    
    def calmar_ratio(self):
        #returns the calmar ratio of the backtest
        
        mdd = self.max_drawdown() * -1
        if mdd != 0:
            annualized_return = self._annualize(self.stats["Return [%]"] / 100)
            calmar_ratio_ = (annualized_return- self.risk_free_return) / mdd

            return calmar_ratio_
        
        else:
            return 0
        