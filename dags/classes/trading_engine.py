import pandas as pd
import os
from dotenv import load_dotenv

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import OrderRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce

from airflow.models import Variable


class TradingEngine:

    def __init__(self):
        # Environment Variables
        api_key = Variable.get("ALPACA_API_KEY")
        secret_key = Variable.get("ALPACA_SECRET_KEY")

        # Clients
        self.trading_client = TradingClient(api_key,secret_key)
    
    def get_account_value(self):
        account = self.trading_client.get_account()

        return account.cash    
        

    def sell_current_positions(self):
        self.trading_client.close_all_positions()


    def buy_new_positions(self, df: pd.DataFrame, total_notional):
        
        for order in df.iterrows():

            symbol = order['symbol']
            notional = total_notional * order['weight']

            order_request = OrderRequest(
                symbol=symbol,
                notional=notional,
                side=OrderSide.BUY,
                type=OrderType.MARKET,
                time_in_force=TimeInForce.DAY
            )

            result = self.trading_client.submit_order(order_request)

            print(result)