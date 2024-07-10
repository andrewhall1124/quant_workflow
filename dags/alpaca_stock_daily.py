import json
import pendulum
import pandas as pd
import numpy as np
import pendulum
from dotenv import load_dotenv

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

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
    start_date=pendulum.datetime(2024, 7, 4),
    catchup=False,
    tags=["example"],
    default_view='graph'
)
def alpaca_stock_daily():

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
    
    @task()
    def extract():

        # Get all current assets
        asset_request = GetAssetsRequest(
            # status = AssetStatus.ACTIVE,
            asset_class = AssetClass.US_EQUITY,
        )

        all_assets = trading_client.get_all_assets(asset_request)

        all_assets = [vars(asset) for asset in all_assets] # Convert objects to dicts

        df = pd.DataFrame(data=all_assets)

        # df = df[df['tradable'] & df['fractionable'] & df['shortable']]

        data_path = "assets.csv"

        df.to_csv(data_path,index=False)

        postgres_hook = PostgresHook(postgres_conn_id="pg_database")
        conn = postgres_hook.get_conn()
        cur = conn.cursor()
        with open(data_path, "r") as file:
            cur.copy_expert(
                "COPY temp_assets FROM STDIN WITH CSV HEADER DELIMITER AS ',' QUOTE '\"'",
                file,
            )
        conn.commit()
 
    # @task()
    # def transform():
    #     return

    # @task()
    # def load():
    #     return


    [create_assets_table, create_temp_assets_table] >> extract() #>> transform() >> load()
    
alpaca_stock_daily()
