
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task, dag

from datetime import datetime, timedelta

@dag(description="DAG in charge of processing customer data",
        start_date=datetime(2021, 1, 1),
        schedule_interval='@daily',
        dagrun_timeout=timedelta(minutes=10),
        tags=['data_science', 'customer'],
        catchup=False    )
def dag_303_taskflow():

    @task.python
    def extract(): # ti = task instance object
        partner_name = "netflix"
        return partner_name

    @task.python
    def process(partner_name):
        print(partner_name)

    process(extract())

dag = dag_303_taskflow()
