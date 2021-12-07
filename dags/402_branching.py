
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
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

def _choosing_pertner_based_on_day(execution_date):
    day = execution_date.day_of_week
    print(day)
    if (day == 1):
        return 'extract_partner_snowflake'
    if (day == 3):
        return 'extract_partner_netflix'
    if (day == 5):
        return 'extract_partner_astronomer'
    
    return 'stop'


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
def dag_402_branching():

    start = DummyOperator(task_id="start")
    stop = DummyOperator(task_id="stop")

    storing = DummyOperator(task_id="storing", trigger_rule='none_failed_or_skipped')

    choosing_pertner_based_on_day = BranchPythonOperator(
        task_id='choosing_pertner_based_on_day',
        python_callable=_choosing_pertner_based_on_day
    )

    choosing_pertner_based_on_day >> stop

    for partner, details in partners.items():
        
        @task.python(task_id=f"extract_{partner}", do_xcom_push=False, multiple_outputs=True)
        def extract(partner_name, partner_path):
            return {"partner_name":partner_name, "partner_path":partner_path}
        
        extracted_values = extract(details['name'], details['path'])
        start >> choosing_pertner_based_on_day >> extracted_values
        process_tasks(extracted_values) >> storing



dag = dag_402_branching()
