import pendulum
import pandas as pd

from airflow.decorators import dag, task, task_group

from classes.db import DB
from classes.model import fip_model
from classes.trading_engine import TradingEngine

@dag(
    schedule='@monthly',
    start_date=pendulum.datetime(2024, 6, 30),
    catchup=False,
    tags=["fip","monthly"],
    default_view='graph'
)
def fip_trading_monthly():
    
    @task
    def get_stock_data(data_interval_end) -> pd.DataFrame:
        db = DB()

        end = data_interval_end.subtract(days=1)
        start = end.subtract(months=13)

        query_string = f'''
            SELECT 
                SYMBOL, 
                TIMESTAMP, 
                CLOSE
            FROM HISTORICAL_DATA 
            WHERE TIMESTAMP BETWEEN '{start}' AND '{end}' 
            ORDER BY SYMBOL, TIMESTAMP;
        '''

        df = db.execute_df(query_string)

        return df
     
    @task
    def compute_portfolio(df: pd.DataFrame) -> pd.DataFrame:
        num_positions = 25
        portfolio = fip_model(df, num_positions)
        return portfolio
    
    @task
    def sell_current_portfolio():
        TradingEngine().sell_current_positions()

    @task
    def cancel_current_orders():
        TradingEngine().cancel_all_orders()

    @task
    def get_account_value():
        return TradingEngine().get_account_value()

    @task
    def buy_new_portfolio(df, total_notional):
        TradingEngine().buy_new_positions(df, total_notional)

    
    data = get_stock_data()
    portfolio = compute_portfolio(data)
    total_notional = cancel_current_orders() >> sell_current_portfolio() >> get_account_value()
    buy_new_portfolio(portfolio, total_notional)
    
    
fip_trading_monthly()
