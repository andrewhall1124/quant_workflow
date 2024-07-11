import psycopg2
from psycopg2 import sql

class DB:
    
    def __init__(self):
        connection_params = {
            'dbname': 'postgres',
            'user': 'airflow',
            'password': 'airflow',
            'host': 'localhost',
            'port': '5432'
        }

        self.conn = psycopg2.connect(**connection_params)
        self.cur = self.conn.cursor()

    def execute(self, query_string):
        self.cur.execute(query_string)
        return self.cur.fetchall()

    def __del__(self):
        self.cur.close()
        self.conn.close()