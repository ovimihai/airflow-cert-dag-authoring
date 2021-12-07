
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task, dag

from datetime import datetime, timedelta
from typing import Dict

@dag(description="DAG in charge of processing customer data",
        start_date=datetime(2021, 1, 1),
        schedule_interval='@daily',
        dagrun_timeout=timedelta(minutes=10),
        tags=['data_science', 'customer'],
        catchup=False    )
def dag_304_taskflow():

    # add multiple_outputs=True for multiple XCOMs - will also push dictionary
    #   prevent push dictionary with do_xcom_push=False
    # or put  -> Dict[str, str] # with this doesn't seem to work for separate args
    @task.python(task_id="extract_partners", do_xcom_push=False, multiple_outputs=True)
    def extract():
        return {"partner_name":"neftlix", "partner_path":"/path/netflix"}

    @task.python
    def process(partner_name, partner_path):
        print(partner_name)
        print(partner_path)

    partner_settings = extract()

    process(partner_settings['partner_name'], partner_settings['partner_path'])

dag = dag_304_taskflow()
