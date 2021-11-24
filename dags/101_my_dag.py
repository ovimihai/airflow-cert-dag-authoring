from airflow import DAG
from datetime import datetime, timedelta

with DAG(dag_id='101my_dag',
         description='',
         start_date=datetime(2021,1,1),
         schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10),
         tags=['data_science', 'customer'],
         catchup=False
         ) as dag:
         None