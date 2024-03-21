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
