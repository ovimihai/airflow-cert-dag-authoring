# ======================================================================
# MERGED DAG FILE
# All DAGs from the `dags/` directory concatenated together.
# Each section is preceded by a heading indicating its source file.
# This is a reference/study file, not meant to be run as-is.
# ======================================================================


# ======================================================================
# FILE: dags/101_my_dag.py
# ======================================================================

from airflow import DAG
from datetime import datetime, timedelta

with DAG(dag_id='101my_dag',
         description='Dag example without any task',
         start_date=datetime(2021,1,1),
         schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10),
         tags=['data_science', 'customer'],
         catchup=False
         ) as dag:
         None


# ======================================================================
# FILE: dags/301_templating.py
# ======================================================================

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from datetime import datetime, timedelta

# https://registry.astronomer.io/providers/postgres/modules/postgresoperator
# https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator
class CustomPostgresOperator(PostgresOperator):

    template_fields = ('sql', 'parameters',)

    def execute(self, context):
        return 0


def _extract(partner_name):
    print(partner_name)

with DAG("301_templating", description="Templating in both variables and files. Checkout Render tab ofr each task.",
        start_date=datetime(2021, 1, 1),
        schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10),
         tags=['data_science', 'customer'],
         catchup=False
         ) as dag:

         extract = PythonOperator(
             task_id="extract",
             python_callable=_extract,
             op_args=["{{ var.json.my_dag_partner.name }}"]
         )

         fetching_data = CustomPostgresOperator(
             task_id="fetching_data",
             sql="sql/301_my_request.sql",   # template_ext https://github.com/apache/airflow/blob/main/airflow/providers/postgres/operators/postgres.py#L46
             parameters={
                 'next_ds': '{{ next_ds }}',
                 'prev_ds': '{{ prev_ds }}',
                 'partner_name': '{{ var.json.my_dag_partner.name }}'
             }
         )


# ======================================================================
# FILE: dags/302_xcoms.py
# ======================================================================

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from datetime import datetime, timedelta

# https://registry.astronomer.io/providers/postgres/modules/postgresoperator
# https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator
class CustomPostgresOperator(PostgresOperator):

    template_fields = ('sql', 'parameters',)



def _extract(partner_name, **kwargs):
    print(partner_name)
    ti = kwargs['ti']
    ti.xcom_push(key="partner_name", value=partner_name)
    # or unnamed
    # return partner_name

def _process(**kwargs):
    ti = kwargs['ti']
    partner_name = ti.xcom_pull(key="partner_name", task_ids="extract")
    print(partner_name)

with DAG("302_xcoms", description="DAG with xcom passing example",
        start_date=datetime(2021, 1, 1),
        schedule_interval='@daily',
         dagrun_timeout=timedelta(minutes=10),
         tags=['data_science', 'customer'],
         catchup=False
         ) as dag:

         extract = PythonOperator(
             task_id="extract",
             python_callable=_extract,
             op_args=['{{ var.json.my_dag_partner.name }}'],
             provide_context=True
         )

         process = PythonOperator(
             task_id="process",
             python_callable=_process
         )

         extract >> process


# ======================================================================
# FILE: dags/303_taskflow.py
# ======================================================================

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


# ======================================================================
# FILE: dags/304_taskflow2.py
# ======================================================================

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


# ======================================================================
# FILE: dags/305_subdags.py
# ======================================================================

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
def dag_305_subdags():

    # add multiple_outputs=True for multiple XCOMs - will also push dictionary
    #   prevent push dictionary with do_xcom_push=False
    # or put  -> Dict[str, str] # with this doesn't seem to work for separate args
    @task.python(task_id="extract_partners", do_xcom_push=False, multiple_outputs=True)
    def extract():
        return {"partner_name":"neftlix", "partner_path":"/path/netflix"}


    process_tasks = SubDagOperator(
        task_id="process_tasks",
        subdag=subdag_factory("dag_305_subdags", "process_tasks", default_args)
    )
    
    extract() >> process_tasks

dag = dag_305_subdags()


# ======================================================================
# FILE: dags/306_tasks_groups.py
# ======================================================================

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


# ======================================================================
# FILE: dags/401_dynamic_tasks.py
# ======================================================================

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


# ======================================================================
# FILE: dags/402_branching.py
# ======================================================================

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


# ======================================================================
# FILE: dags/403_dependencies.py
# ======================================================================

from airflow import DAG
from airflow.decorators import task, dag
from airflow.operators.dummy import DummyOperator

from airflow.models.baseoperator import cross_downstream, chain
from datetime import datetime, timedelta

default_args = {
    "start_date": datetime(2021, 1, 1)
}

@dag(description="DAG in charge of processing customer data",
        default_args=default_args,
        schedule_interval='@daily',
        dagrun_timeout=timedelta(minutes=10),
        catchup=False, max_active_runs=1)
def dag_403_dependencies():

    t1 = DummyOperator(task_id="t1")
    t2 = DummyOperator(task_id="t2")
    t3 = DummyOperator(task_id="t3")
    t4 = DummyOperator(task_id="t4")
    t5 = DummyOperator(task_id="t5")
    t6 = DummyOperator(task_id="t6")
    

    cross_downstream([t1, t2, t3], [t4, t5, t6])


    x1 = DummyOperator(task_id="x1")
    x2 = DummyOperator(task_id="x2")
    x3 = DummyOperator(task_id="x3")
    x4 = DummyOperator(task_id="x4")
    x5 = DummyOperator(task_id="x5")
    x6 = DummyOperator(task_id="x6")

    chain(x1, [x2,x3], [x4,x5], x6)

    y1 = DummyOperator(task_id="y1")
    y2 = DummyOperator(task_id="y2")
    y3 = DummyOperator(task_id="y3")
    y4 = DummyOperator(task_id="y4")
    y5 = DummyOperator(task_id="y5")
    y6 = DummyOperator(task_id="y6")

    cross_downstream([y2,y3], [y4,y5])
    chain(y1, y2, y5, y6)


dag = dag_403_dependencies()


# ======================================================================
# FILE: dags/404_tasks_priority.py
# ======================================================================

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
def dag_404_task_priority():

    start = DummyOperator(task_id="start")

    storing = DummyOperator(task_id="storing", trigger_rule='none_failed_or_skipped')

    for partner, details in partners.items():
        
        @task.python(task_id=f"extract_{partner}", 
                priority_weight=details['priority'],
                pool='partner_pool',
                do_xcom_push=False, multiple_outputs=True)
        def extract(partner_name, partner_path):
            time.sleep(3)
            return {"partner_name":partner_name, "partner_path":partner_path}
        
        extracted_values = extract(details['name'], details['path'])
        start >> extracted_values
        process_tasks(extracted_values) >> storing



dag = dag_404_task_priority()


# ======================================================================
# FILE: dags/405_depends_on_past.py
# ======================================================================

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


# ======================================================================
# FILE: dags/406_sensors.py
# ======================================================================

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy import DummyOperator
from airflow.sensors.date_time import DateTimeSensor

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
def dag_406_sensors():

    start = DummyOperator(task_id="start")

    delay = DateTimeSensor(
        task_id="delay",
        # change date to match your desiredtime
        target_time="{{ next_execution_date.replace(hour=17,minute=8) }}",
        poke_interval=60 
    )

    storing = DummyOperator(task_id="storing", trigger_rule='none_failed_or_skipped')

    for partner, details in partners.items():
        
        @task.python(task_id=f"extract_{partner}", 
                priority_weight=details['priority'],
                pool='partner_pool',
                do_xcom_push=False, multiple_outputs=True)
        def extract(partner_name, partner_path):
            time.sleep(3)
            return {"partner_name":partner_name, "partner_path":partner_path}
        
        extracted_values = extract(details['name'], details['path'])
        start >> delay >> extracted_values
        process_tasks(extracted_values) >> storing



dag = dag_406_sensors()


# ======================================================================
# FILE: dags/subdag/subdag_factory.py
# ======================================================================

from airflow.models import DAG
from airflow.decorators import task
from airflow.operators.python import get_current_context

@task.python
def process_a():
    ti = get_current_context()['ti']
    print(ti.xcom_pull(key="partner_name", task_ids="extract_partners", dag_id="dag_305_taskflow"))
    print(ti.xcom_pull(key="partner_path", task_ids="extract_partners", dag_id="dag_305_taskflow"))

@task.python
def process_b():
    ti = get_current_context()['ti']
    print(ti.xcom_pull(key="partner_name", task_ids="extract_partners", dag_id="dag_305_taskflow"))
    print(ti.xcom_pull(key="partner_path", task_ids="extract_partners", dag_id="dag_305_taskflow"))

@task.python
def process_c():
    ti = get_current_context()['ti']
    print(ti.xcom_pull(key="partner_name", task_ids="extract_partners", dag_id="dag_305_taskflow"))
    print(ti.xcom_pull(key="partner_path", task_ids="extract_partners", dag_id="dag_305_taskflow"))

def subdag_factory(parent_dag_id, subdag_dag_id, default_args):

    with DAG(f"{parent_dag_id}.{subdag_dag_id}", default_args=default_args) as dag:

        process_a()
        process_b()
        process_c()

        return dag


# ======================================================================
# FILE: dags/example-dag.py
# ======================================================================

from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.version import version
from datetime import datetime, timedelta


def my_custom_function(ts,**kwargs):
    """
    This can be any python code you want and is called from the python operator. The code is not executed until
    the task is run by the airflow scheduler.
    """
    print(f"I am task number {kwargs['task_number']}. This DAG Run execution date is {ts} and the current time is {datetime.now()}")
    print('Here is the full DAG Run context. It is available because provide_context=True')
    print(kwargs)


# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Using a DAG context manager, you don't have to specify the dag property of each task
with DAG('example_dag',
         start_date=datetime(2024, 3, 21),
         max_active_runs=3,
         schedule_interval=timedelta(hours=1),  # https://airflow.apache.org/docs/stable/scheduler.html#dag-runs
         default_args=default_args,
         # catchup=False # enable if you don't want historical dag runs to run
         ) as dag:

    t0 = DummyOperator(
        task_id='start'
    )

    t1 = DummyOperator(
        task_id='group_bash_tasks'
    )
    t2 = BashOperator(
        task_id='bash_print_date1',
        bash_command='sleep $[ ( $RANDOM % 30 )  + 1 ]s && date')
    t3 = BashOperator(
        task_id='bash_print_date2',
        bash_command='sleep $[ ( $RANDOM % 30 )  + 1 ]s && date')

    # generate tasks with a loop. task_id must be unique
    for task in range(5):
        if version.startswith('2'):
            tn = PythonOperator(
                task_id=f'python_print_date_{task}',
                python_callable=my_custom_function,  # make sure you don't include the () of the function
                op_kwargs={'task_number': task},
            )
        else:
            tn = PythonOperator(
                task_id=f'python_print_date_{task}',
                python_callable=my_custom_function,  # make sure you don't include the () of the function
                op_kwargs={'task_number': task},
                provide_context=True,
            )


        t0 >> tn # indented inside for loop so each task is added downstream of t0

    t0 >> t1
    t1 >> [t2, t3] # lists can be used to specify multiple tasks


# ======================================================================
# FILE: dags/example_dag_basic.py
# ======================================================================

import json
from pendulum import datetime

from airflow.decorators import (
    dag,
    task,
)  # DAG and task decorators for interfacing with the TaskFlow API


# When using the DAG decorator, The "dag_id" value defaults to the name of the function
# it is decorating if not explicitly set. In this example, the "dag_id" value would be "example_dag_basic".
@dag(
    # This defines how often your DAG will run, or the schedule by which your DAG runs. In this case, this DAG
    # will run daily
    schedule="@daily",
    # This DAG is set to run for the first time on January 1, 2023. Best practice is to use a static
    # start_date. Subsequent DAG runs are instantiated based on the schedule
    start_date=datetime(2023, 1, 1),
    # When catchup=False, your DAG will only run the latest run that would have been scheduled. In this case, this means
    # that tasks will not be run between January 1, 2023 and 30 mins ago. When turned on, this DAG's first
    # run will be for the next 30 mins, per the its schedule
    catchup=False,
    default_args={
        "retries": 2,  # If a task fails, it will retry 2 times.
    },
    tags=["example"],
)  # If set, this tag is shown in the DAG view of the Airflow UI
def example_dag_basic():
    """
    ### Basic ETL Dag
    This is a simple ETL data pipeline example that demonstrates the use of
    the TaskFlow API using three simple tasks for extract, transform, and load.
    For more information on Airflow's TaskFlow API, reference documentation here:
    https://airflow.apache.org/docs/apache-airflow/stable/tutorial_taskflow_api.html
    """

    @task()
    def extract():
        """
        #### Extract task
        A simple "extract" task to get data ready for the rest of the
        pipeline. In this case, getting data is simulated by reading from a
        hardcoded JSON string.
        """
        data_string = '{"1001": 301.27, "1002": 433.21, "1003": 502.22}'

        order_data_dict = json.loads(data_string)
        return order_data_dict

    @task(
        multiple_outputs=True
    )  # multiple_outputs=True unrolls dictionaries into separate XCom values
    def transform(order_data_dict: dict):
        """
        #### Transform task
        A simple "transform" task which takes in the collection of order data and
        computes the total order value.
        """
        total_order_value = 0

        for value in order_data_dict.values():
            total_order_value += value

        return {"total_order_value": total_order_value}

    @task()
    def load(total_order_value: float):
        """
        #### Load task
        A simple "load" task that takes in the result of the "transform" task and prints it out,
        instead of saving it to end user review
        """

        print(f"Total order value is: {total_order_value:.2f}")

    order_data = extract()
    order_summary = transform(order_data)
    load(order_summary["total_order_value"])


example_dag_basic()


# ======================================================================
# FILE: dags/example_dag_advanced.py
# ======================================================================

from pendulum import datetime, duration

# Airflow Operators are templates for tasks and encompass the logic that your DAG will actually execute.
# To use an operator in your DAG, you first have to import it.
# To learn more about operators, see: https://registry.astronomer.io/.

# DAG and task decorators for interfacing with the TaskFlow API
from airflow.decorators import dag, task, task_group

# A function that sets sequential dependencies between tasks including lists of tasks
from airflow.models.baseoperator import chain

from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.weekday import BranchDayOfWeekOperator

# Used to label node edges in the Airflow UI
from airflow.utils.edgemodifier import Label

# Used to determine the day of the week
from airflow.utils.weekday import WeekDay


"""
This DAG is intended to demonstrate a number of core Apache Airflow concepts that are central to the pipeline
authoring experience, including the TaskFlow API, Edge Labels, Jinja templating, branching,
generating tasks within a loop, task groups, and trigger rules.

First, this DAG checks if the current day is a weekday or weekend. Next, the DAG checks which day of the week
it is. Lastly, the DAG prints out a bash statement based on which day it is. On Tuesday, for example, the DAG
prints "It's Tuesday and I'm busy with studying".

This DAG uses the following operators:

BashOperator -
    Executes a Bash script, command, or set of commands.

    See more info about this operator here:
        https://registry.astronomer.io/providers/apache-airflow/modules/bashoperator

EmptyOperator -
    Does nothing but can be used to structure your DAG.

    See more info about this operator here:
        https://registry.astronomer.io/providers/apache-airflow/modules/emptyoperator

BranchDayOfWeekOperator -
    Branches into one of two lists of tasks depending on the current day.

    See more info about this operator here:
        https://registry.astronomer.io/providers/apache-airflow/modules/branchdayofweekoperator
"""

# Reference data that defines "weekday" as well as the activity assigned to each day of the week
DAY_ACTIVITY_MAPPING = {
    "monday": {"is_weekday": True, "activity": "guitar lessons"},
    "tuesday": {"is_weekday": True, "activity": "studying"},
    "wednesday": {"is_weekday": True, "activity": "soccer practice"},
    "thursday": {"is_weekday": True, "activity": "contributing to Airflow"},
    "friday": {"is_weekday": True, "activity": "family dinner"},
    "saturday": {"is_weekday": False, "activity": "going to the beach"},
    "sunday": {"is_weekday": False, "activity": "sleeping in"},
}

# The TaskFlow API is also used in a number of tasks within this DAG. Check out of the TaskFlow API tutorial
# to learn more.
#   https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html


# This is the TaskFlow equivalent of the PythonOperator:
#   https://registry.astronomer.io/providers/apache-airflow/modules/pythonoperator
@task(
    # By default the function name is used as the `task_id`, but it can be overriden if desired.
    task_id="going_to_the_beach",
    multiple_outputs=True,  # multiple_outputs=True unrolls dictionaries into separate XCom values
)
def _going_to_the_beach() -> dict[str, str]:
    return {
        "subject": "Beach day!",
        "body": "It's Saturday and I'm heading to the beach.<br>Come join me!",
    }


# This is the TaskFlow API equivalent to the BranchPythonOperator:
#   https://registry.astronomer.io/providers/apache-airflow/modules/branchpythonoperator
# The task retrieves the activity from the "DAY_ACTIVITY_MAPPING" dictionary.
@task.branch
def get_activity(day_name: str) -> str:
    activity_id = DAY_ACTIVITY_MAPPING[day_name]["activity"].replace(" ", "_")

    if DAY_ACTIVITY_MAPPING[day_name]["is_weekday"]:
        return f"weekday_activities.{activity_id}"

    return f"weekend_activities.{activity_id}"


# This the TaskFlow API equivalent to the PythonVirtualEnvOperator:
#   https://registry.astronomer.io/providers/apache-airflow/modules/pythonvirtualenvoperator
@task.virtualenv(requirements=["beautifulsoup4==4.11.2"])
def inviting_friends(subject: str, body: str) -> None:
    from bs4 import BeautifulSoup

    print("Inviting friends...")
    html_doc = f"<title>{subject}</title><p>{body}</p>"
    soup = BeautifulSoup(html_doc, "html.parser")
    print(soup.prettify())


# When using the DAG decorator, the "dag" argument doesn't need to be specified for each task.
# The "dag_id" value defaults to the name of the function it is decorating if not explicitly set.
# In this example, the "dag_id" value would be "example_dag_advanced".
@dag(
    # This DAG is set to run for the first time on January 1, 2023.
    # Best practice is to use a static start_date.
    # Subsequent DAG runs are instantiated based on the "schedule" parameter below.
    start_date=datetime(2023, 1, 1),
    # This defines how many instantiations of this DAG (DAG Runs) can execute concurrently. In this case,
    # we're only allowing 1 DAG run at any given time, as opposed to allowing multiple overlapping DAG runs.
    max_active_runs=1,
    # This defines how often your DAG will run, or the schedule by which DAG runs are created. It can be
    # defined as a cron expression, custom timetable, existing presets or using the Dataset feature.
    # This DAG uses a preset to run daily.
    schedule="@daily",
    # Default settings applied to all tasks within the DAG; can be overwritten at the task level.
    default_args={
        "owner": "community",  # Defines the value of the "owner" column in the DAG view of the Airflow UI
        "retries": 2,  # If a task fails, it will retry 2 times.
        "retry_delay": duration(
            minutes=3
        ),  # A task that fails will wait 3 minutes to retry.
    },
    default_view="graph",  # This defines the default view for this DAG in the Airflow UI
    # When catchup=False, your DAG will only run for the latest schedule interval. In this case, this means
    # that tasks will not be run between January 1st, 2023 and 1 day ago. When turned on, this DAG's first run
    # will be for today, per the @daily schedule
    catchup=False,
    tags=["example"],  # If set, this tag is shown in the DAG view of the Airflow UI
)
def example_dag_advanced():
    # EmptyOperator placeholder for first task
    begin = EmptyOperator(task_id="begin")
    # Last task will only trigger if all upstream tasks have succeeded or been skipped
    end = EmptyOperator(task_id="end", trigger_rule="none_failed")

    # This task checks which day of the week it is
    check_day_of_week = BranchDayOfWeekOperator(
        task_id="check_day_of_week",
        week_day={WeekDay.SATURDAY, WeekDay.SUNDAY},  # This checks day of week
        follow_task_ids_if_true="weekend",  # Next task if criteria is met
        follow_task_ids_if_false="weekday",  # Next task if criteria is not met
        use_task_execution_day=True,  # If True, uses task’s execution day to compare with is_today
    )

    weekend = EmptyOperator(task_id="weekend")  # "weekend" placeholder task
    weekday = EmptyOperator(task_id="weekday")  # "weekday" placeholder task

    # Templated value for determining the name of the day of week based on the start date of the DAG Run
    day_name = "{{ dag_run.start_date.strftime('%A').lower() }}"

    # Begin weekday tasks.
    # Tasks within this TaskGroup (weekday tasks) will be grouped together in the Airflow UI
    @task_group
    def weekday_activities():
        # TaskFlow functions can also be reused which is beneficial if you want to use the same callable for
        # multiple tasks and want to use different task attributes.
        # See this tutorial for more information:
        #   https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html#reusing-a-decorated-task
        which_weekday_activity_day = get_activity.override(
            task_id="which_weekday_activity_day"
        )(day_name)

        for day, day_info in DAY_ACTIVITY_MAPPING.items():
            if day_info["is_weekday"]:
                day_of_week = Label(label=day)
                activity = day_info["activity"]

                # This task prints the weekday activity to bash
                do_activity = BashOperator(
                    task_id=activity.replace(" ", "_"),
                    # This is the Bash command to run
                    bash_command=f"echo It's {day.capitalize()} and I'm busy with {activity}.",
                )

                # Declaring task dependencies within the "TaskGroup" via the classic bitshift operator.
                which_weekday_activity_day >> day_of_week >> do_activity

    # Begin weekend tasks
    # Tasks within this TaskGroup will be grouped together in the UI
    @task_group
    def weekend_activities():
        which_weekend_activity_day = get_activity.override(
            task_id="which_weekend_activity_day"
        )(day_name)

        # Labels that will appear in the Graph view of the Airflow UI
        saturday = Label(label="saturday")
        sunday = Label(label="sunday")

        # This task runs the Sunday activity of sleeping for a random interval between 1 and 30 seconds
        sleeping_in = BashOperator(
            task_id="sleeping_in", bash_command="sleep $[ (1 + $RANDOM % 30) ]s"
        )

        going_to_the_beach = _going_to_the_beach()  # Calling the TaskFlow task

        # Because the "_going_to_the_beach()" function has "multiple_outputs" enabled, each dict key is
        # accessible as their own "XCom" key.
        _inviting_friends = inviting_friends(
            subject=going_to_the_beach["subject"], body=going_to_the_beach["body"]
        )

        # Using "chain()" here for list-to-list dependencies which are not supported by the bitshift
        # operator and to simplify the notation for the desired dependency structure.
        chain(
            which_weekend_activity_day,
            [saturday, sunday],
            [going_to_the_beach, sleeping_in],
        )

    # Call the @task_group TaskFlow functions to instantiate them in the DAG
    _weekday_activities = weekday_activities()
    _weekend_activities = weekend_activities()

    # High-level dependencies between tasks
    chain(
        begin,
        check_day_of_week,
        [weekday, weekend],
        [_weekday_activities, _weekend_activities],
        end,
    )

    # Task dependency created by XComArgs:
    # going_to_the_beach >> inviting_friends


example_dag_advanced()
