
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task, dag
from airflow.utils.task_group import TaskGroup

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
def dag_306_taskflow():

    # add multiple_outputs=True for multiple XCOMs - will also push dictionary
    #   prevent push dictionary with do_xcom_push=False
    # or put  -> Dict[str, str] # with this doesn't seem to work for separate args
    @task.python(task_id="extract_partners", do_xcom_push=False, multiple_outputs=True)
    def extract():
        return {"partner_name":"neftlix", "partner_path":"/path/netflix"}

    partner_settings = extract()

    with TaskGroup(group_id="process_tasks") as process_tasks:
        @task.python
        def process_a(partner_name, partner_path):
            print(partner_name)
            print(partner_path)

        @task.python
        def process_b(partner_name, partner_path):
            print(partner_name)
            print(partner_path)

        @task.python
        def process_c(partner_name, partner_path):
            print(partner_name)
            print(partner_path)

        process_a(partner_settings['partner_name'], partner_settings['partner_path'])
        process_b(partner_settings['partner_name'], partner_settings['partner_path'])
        process_c(partner_settings['partner_name'], partner_settings['partner_path'])


dag = dag_306_taskflow()
