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
