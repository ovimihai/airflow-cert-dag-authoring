
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task, dag
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy import DummyOperator

from datetime import datetime, timedelta
from typing import Dict
from subdag.subdag_factory import subdag_factory


partners = {
    "partner_snowflake": {"name": "snowflake", "path":"/partners/snowflake"},
    "partner_netflix": {"name": "netflix", "path":"/partners/netflix"},
    "partner_astronomer": {"name": "astronomer", "path":"/partners/astronomer"},
}

default_args = {
    "start_date": datetime(2021, 1, 1)
}

@task.python
def process_a(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

@task.python
def process_b(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

@task.python
def check_a():
    print("checking")
def check_b():
    print("checking")
def check_c():
    print("checking")


@task.python
def process_c(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

def process_tasks(partner_settings):
    with TaskGroup(group_id="process_tasks", add_suffix_on_collision=True) as process_tasks:
        with TaskGroup(group_id="test_tasks") as process_tasks:
            check_a()

        process_a(partner_settings['partner_name'], partner_settings['partner_path'])
        process_b(partner_settings['partner_name'], partner_settings['partner_path'])
        process_c(partner_settings['partner_name'], partner_settings['partner_path'])

@dag(description="DAG in charge of processing customer data",
        default_args=default_args,
        schedule_interval='@daily',
        dagrun_timeout=timedelta(minutes=10),
        tags=['data_science', 'customer'],
        catchup=False    )
def dag_401_dynamic():

    start = DummyOperator(task_id="start")

    for partner, details in partners.items():
        
        @task.python(task_id=f"extract_{partner}", do_xcom_push=False, multiple_outputs=True)
        def extract(partner_name, partner_path):
            return {"partner_name":partner_name, "partner_path":partner_path}
        
        extracted_values = extract(details['name'], details['path'])
        start >> extracted_values
        process_tasks(extracted_values)


dag = dag_401_dynamic()
