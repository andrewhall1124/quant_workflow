import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

from airflow.providers.postgres.hooks.postgres import PostgresHook

class DB:
    
    def __init__(self):
        pg_hook = PostgresHook(postgres_conn_id='pg_database')
        self.conn = pg_hook.get_conn()

    def execute(self, query_string):
        self.cur.execute(query_string)
        return self.cur.fetchall()
    
    def execute_df(self,query_string):
        df = pd.read_sql_query(query_string, self.conn)
        return df