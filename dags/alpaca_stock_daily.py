import json
import pendulum
from airflow.decorators import dag, task

@dag(
    schedule='@daily',
    start_date=pendulum.datetime(2024, 7, 4),
    catchup=False,
    tags=["example"],
    default_view='graph'
)
def alpaca_stock_daily():
    
    @task()
    def extract():
        return
 
    @task()
    def transform():
        return

    @task()
    def load():
        return


    extract() >> transform() >> load()
    
alpaca_stock_daily()
