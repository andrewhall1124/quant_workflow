# This class should only require a pandas dataframe with dates and daily returns (maybe prices)
# In the future this class will pull in daily returns for a specified benchmark/market to compute alpha and other metrics
# The daily risk free rate will also be pulled in in the future to compute the sharpe ratio via the FRED data api

import statsmodels.api as sm
import numpy as np
import pandas as pd

TRADING_DAYS = 252


class Performance:

    def __init__(self, returns: pd.Series):
        """
        Create an instance of the performance class by instantiating it with a vector of daily returns representing the portfolios performance.
        """

        self.return_vector = returns

    
    def total_return(self, annualized: bool = True) -> float:
        """
    Calculate the total return of a security or portfolio.

    Parameters:
    - returns: Daily returns of the security or portfolio.

    Returns:
    - float: total return.
    """
        compounded_return = (1 + self.returns).prod() - 1

        if annualized:
            periods = len(self.returns)

            annualized_return = (1 + compounded_return) * (TRADING_DAYS / periods) - 1

            return annualized_return

        else:
            return compounded_return



    def volatility(self, annualized: bool = True) -> float:
        """
    Calculate the volatility of a security or portfolio.

    Parameters:
    - returns: Daily returns of the security or portfolio.

    Returns:
    - float: volatility (annualized).
    """

        standard_deviation = self.returns.std()

        return standard_deviation * np.sqrt(TRADING_DAYS) if annualized else standard_deviation

