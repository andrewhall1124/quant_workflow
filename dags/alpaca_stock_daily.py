import pendulum
import pandas as pd

from airflow.decorators import dag, task, task_group
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

# Arguments
default_args = {
    'retries': 6,
    'retry_delay': pendulum.duration(hours=1),
}

@dag(
    schedule='@daily',
    start_date=pendulum.datetime(2024, 6, 30),
    catchup=True,
    tags=["alpaca","daily"],
    default_view='graph',
    default_args=default_args
)
def alpaca_stock_daily():

    @task_group
    def download_and_load_assets():

        @task_group
        def setup():

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
        def extract(run_id):

            # Get all assets
            asset_request = GetAssetsRequest(
                asset_class = AssetClass.US_EQUITY,
            )

            all_assets = trading_client.get_all_assets(asset_request)

            all_assets = [vars(asset) for asset in all_assets] # Convert objects to dicts

            df = pd.DataFrame(data=all_assets)

            df['insert_id'] = run_id
            df['update_id'] = run_id

            data_path = "assets.csv"

            df.to_csv(data_path,index=False)

            postgres_hook = PostgresHook(postgres_conn_id="pg_database")
            conn = postgres_hook.get_conn()
            cur = conn.cursor()
            with open(data_path, "r") as file:
                cur.copy_expert(
                    f"COPY \"TEMP_ASSETS_{run_id}\" FROM STDIN WITH CSV HEADER DELIMITER AS ',' QUOTE '\"'",
                    file,
                )
            conn.commit()


        load = PostgresOperator(
            task_id="load",
            postgres_conn_id="pg_database",
        sql="sql/merge_temp_into_assets_table.sql",
        )

        cleanup = PostgresOperator(
            task_id="cleanup",
            postgres_conn_id="pg_database",
            sql="DROP TABLE \"TEMP_ASSETS_{{run_id}}\"",
        )

        setup() >> extract() >> load >> cleanup
    
    @task_group
    def download_and_load_historical_data():

        @task_group
        def setup():

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
        def get_current_symbols():
            query = """
                SELECT DISTINCT SYMBOL FROM ASSETS WHERE STATUS = 'active' AND TRADABLE = TRUE AND FRACTIONABLE = TRUE AND SHORTABLE = TRUE;
            """

            postgres_hook = PostgresHook(postgres_conn_id="pg_database")
            conn = postgres_hook.get_conn()
            cur = conn.cursor()
            cur.execute(query)            
            symbols = [row[0] for row in cur.fetchall()]
            conn.commit()
            return symbols
        
        @task
        def extract(symbols, data_interval_start, data_interval_end, run_id):
            # Parameters
            end = data_interval_end
            start = data_interval_start

            # Get previous days market data
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

            df['insert_id'] = run_id
            df['update_id'] = run_id

            data_path = "historical_data.csv"

            df.to_csv(data_path,index=False)

            postgres_hook = PostgresHook(postgres_conn_id="pg_database")
            conn = postgres_hook.get_conn()
            cur = conn.cursor()
            with open(data_path, "r") as file:
                cur.copy_expert(
                    f"COPY \"TEMP_HISTORICAL_DATA_{run_id}\" FROM STDIN WITH CSV HEADER DELIMITER AS ',' QUOTE '\"'",
                    file,
                )
            conn.commit()

        load = PostgresOperator(
            task_id="load",
            postgres_conn_id="pg_database",
            sql="sql/merge_temp_into_historical_data_table.sql",
        )

        cleanup = PostgresOperator(
            task_id="cleanup",
            postgres_conn_id="pg_database",
            sql="DROP TABLE \"TEMP_HISTORICAL_DATA_{{run_id}}\"",
        )

        
        symbols = get_current_symbols()
        
        setup() >> extract(symbols) >> load >> cleanup


    download_and_load_assets() >> download_and_load_historical_data()
    
alpaca_stock_daily()
