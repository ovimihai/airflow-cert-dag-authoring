
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task, dag
from airflow.operators.subdag import SubDagOperator

from datetime import datetime, timedelta
from typing import Dict
from subdag.subdag_factory import subdag_factory

default_args = {
    "start_date": datetime(2021, 1, 1)
}

@dag(description="DAG in charge of processing customer data",
        default_args=default_args,
        schedule_interval='@daily',
        dagrun_timeout=timedelta(minutes=10),
        tags=['data_science', 'customer'],
        catchup=False    )
def dag_305_taskflow():

    # add multiple_outputs=True for multiple XCOMs - will also push dictionary
    #   prevent push dictionary with do_xcom_push=False
    # or put  -> Dict[str, str] # with this doesn't seem to work for separate args
    @task.python(task_id="extract_partners", do_xcom_push=False, multiple_outputs=True)
    def extract():
        return {"partner_name":"neftlix", "partner_path":"/path/netflix"}


    process_tasks = SubDagOperator(
        task_id="process_tasks",
        subdag=subdag_factory("dag_305_taskflow", "process_tasks", default_args)
    )
    
    extract() >> process_tasks

dag = dag_305_taskflow()
