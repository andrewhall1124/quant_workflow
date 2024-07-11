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
    schedule='@monthly',
    start_date=pendulum.datetime(2016, 1, 1),
    catchup=True,
    tags=["alpaca", "history", "monthly"],
    default_view='graph'
)
def alpaca_stock_history():

    with TaskGroup("get_all_assets") as get_all_assets:

        with TaskGroup("setup") as setup:

            create_assets_table = PostgresOperator(
            task_id="create_assets_table",
            postgres_conn_id="pg_database",
            sql="sql/create_assets_table.sql",
            )

            create_temp_assets_table = PostgresOperator(
                task_id="create_temp_assets_table",
                postgres_conn_id="pg_database",
            sql="sql/create_temp_assets_table.sql",
            )

            [create_assets_table, create_temp_assets_table]   
            
        @task()
        def extract():

            # Get all assets
            asset_request = GetAssetsRequest(
                asset_class = AssetClass.US_EQUITY,
            )

            all_assets = trading_client.get_all_assets(asset_request)

            all_assets = [vars(asset) for asset in all_assets] # Convert objects to dicts

            df = pd.DataFrame(data=all_assets)

            data_path = "assets.csv"

            df.to_csv(data_path,index=False)

            postgres_hook = PostgresHook(postgres_conn_id="pg_database")
            conn = postgres_hook.get_conn()
            cur = conn.cursor()
            with open(data_path, "r") as file:
                cur.copy_expert(
                    "COPY TEMP_ASSETS FROM STDIN WITH CSV HEADER DELIMITER AS ',' QUOTE '\"'",
                    file,
                )
            conn.commit()


        load = PostgresOperator(
            task_id="load",
            postgres_conn_id="pg_database",
        sql="sql/merge_temp_into_assets_table.sql",
        )

        setup >> extract() >> load
    
    @task_group
    def get_historical_data():

        with TaskGroup("setup") as setup:

            create_assets_table = PostgresOperator(
            task_id="create_historical_data_table",
            postgres_conn_id="pg_database",
            sql="sql/create_historical_data_table.sql",
            )

            create_temp_assets_table = PostgresOperator(
                task_id="create_temp_historical_data_table",
                postgres_conn_id="pg_database",
            sql="sql/create_temp_historical_data_table.sql",
            )

            [create_assets_table, create_temp_assets_table]  

        @task
        def get_all_symbols():
            query = """
                SELECT DISTINCT SYMBOL FROM ASSETS WHERE TRADABLE = true AND FRACTIONABLE = true AND SHORTABLE = true;
            """

            postgres_hook = PostgresHook(postgres_conn_id="pg_database")
            conn = postgres_hook.get_conn()
            cur = conn.cursor()
            cur.execute(query)            
            symbols = [row[0] for row in cur.fetchall()]
            conn.commit()
            return symbols



        @task
        def extract(symbols, data_interval_start, data_interval_end):
            # Parameters
            end = data_interval_end
            start = data_interval_start

            bars_request = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=TimeFrame(1,TimeFrameUnit.Day),
                start=start,
                end=end,
                adjustment=Adjustment.ALL,
            )

            bars = data_client.get_stock_bars(bars_request)

            df = bars.df

            df = df.reset_index()

            data_path = "historical_data.csv"

            df.to_csv(data_path,index=False)

            postgres_hook = PostgresHook(postgres_conn_id="pg_database")
            conn = postgres_hook.get_conn()
            cur = conn.cursor()
            with open(data_path, "r") as file:
                cur.copy_expert(
                    "COPY TEMP_HISTORICAL_DATA FROM STDIN WITH CSV HEADER DELIMITER AS ',' QUOTE '\"'",
                    file,
                )
            conn.commit()

        load = PostgresOperator(
            task_id="load",
            postgres_conn_id="pg_database",
            sql="sql/merge_temp_into_historical_data_table.sql",
        )

        
        symbols = get_all_symbols()
        
        setup >> extract(symbols) >> load


    get_all_assets >> get_historical_data()
    
alpaca_stock_history()
