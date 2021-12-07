
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
