
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy import DummyOperator

from datetime import datetime, timedelta
from typing import Dict
from subdag.subdag_factory import subdag_factory
import time

partners = {
    "partner_snowflake": {"name": "snowflake", "path":"/partners/snowflake", "priority":2},
    "partner_netflix": {"name": "netflix", "path":"/partners/netflix", "priority":3},
    "partner_astronomer": {"name": "astronomer", "path":"/partners/astronomer", "priority":1},
}

default_args = {
    "start_date": datetime(2021, 1, 1),
    "retries": 0
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
def process_c(partner_name, partner_path):
    print(partner_name)
    print(partner_path)

@task.python
def check_a():
    print("checking")
def check_b():
    print("checking")
def check_c():
    print("checking")


def process_tasks(partner_settings):
    with TaskGroup(group_id="process_tasks", add_suffix_on_collision=True) as process_tasks:
        with TaskGroup(group_id="test_tasks") as process_tasks:
            check_a()
            check_b()
            check_c()

        process_a(partner_settings['partner_name'], partner_settings['partner_path'])
        process_b(partner_settings['partner_name'], partner_settings['partner_path'])
        process_c(partner_settings['partner_name'], partner_settings['partner_path'])

    return process_tasks

@dag(description="DAG in charge of processing customer data",
        default_args=default_args,
        schedule_interval='@daily',
        dagrun_timeout=timedelta(minutes=10),
        tags=['data_science', 'customer'],
        catchup=False, max_active_runs=1)
def dag_405_depends_on_past():

    start = DummyOperator(task_id="start")

    storing = DummyOperator(task_id="storing", trigger_rule='none_failed_or_skipped')

    for partner, details in partners.items():
        
        @task.python(task_id=f"extract_{partner}", 
                depends_on_past=True,
                priority_weight=details['priority'],
                pool='partner_pool',
                do_xcom_push=False, multiple_outputs=True)
        def extract(partner_name, partner_path):
            raise ValueError("failed")
            return {"partner_name":partner_name, "partner_path":partner_path}
        
        extracted_values = extract(details['name'], details['path'])
        start >> extracted_values
        process_tasks(extracted_values) >> storing



dag = dag_405_depends_on_past()
