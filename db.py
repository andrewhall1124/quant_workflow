import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

class DB:
    
    def __init__(self):
        load_dotenv()


        dbname = os.getenv("POSTGRES_DB")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")

        connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }

        # connection_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

        self.conn = psycopg2.connect(**connection_params)
        self.cur = self.conn.cursor()
        # self.engine = create_engine(connection_url)


    def execute(self, query_string):
        self.cur.execute(query_string)
        return self.cur.fetchall()
    
    def execute_df(self,query_string):
        df = pd.read_sql_query(query_string, self.conn)
        return df


    def __del__(self):
        self.cur.close()
        self.conn.close()
        self.engine.dispose()