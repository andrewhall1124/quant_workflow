import json
import pendulum
import pandas as pd
import numpy as np
import pendulum
from dotenv import load_dotenv

from airflow.decorators import dag, task, task_group
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.task_group import TaskGroup

from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest 
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetStatus
from alpaca.trading.enums import AssetClass
from alpaca.data.enums import Adjustment
from alpaca.data.timeframe import TimeFrameUnit


# Environment Variables
api_key = Variable.get("ALPACA_API_KEY")
secret_key = Variable.get("ALPACA_SECRET_KEY")


# Clients
data_client = StockHistoricalDataClient(api_key,secret_key)
trading_client = TradingClient(api_key,secret_key)

@dag(
    schedule='@daily',
    start_date=pendulum.datetime(2016, 1, 1),
    catchup=False,
    tags=["alpaca", "history"],
    default_view='graph'
)
def testing():

    @task
    def print_kwargs(**kwargs):
        print(kwargs)

   
    print_kwargs()
testing()