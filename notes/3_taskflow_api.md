# TaskFlow Api

## Templating

- templated params are defined in the Operator [template_fields](https://github.com/apache/airflow/blob/main/airflow/operators/python.py#L134), [template_ext](https://github.com/apache/airflow/blob/main/airflow/providers/postgres/operators/postgres.py#L46)
- for PythonOperator they are: templates_dict, op_args and op_kwargs
- for PostgresOperator they are sql and the .sql extension
- syntax: `param: '{{ templated_param }}'` or `param: 'path/to_file.ext'`

## XCOMs

- share data between tasks
- push XCOM -> store in metadata database -> pull XCOM
- `ti.xcom_push(key="partner_name", value=partner_name)` 
    - OR just return in an Operator and pull with key `return_value` or None
- `ti.xcom_pull(key="partner_name", task_ids="extract")`
- can push dictionaries -> JSON
- limitations:
    - size: sqlLite 2GB, Postgres 1GB, MySQL 64kB
    - can be increased with [XCOM Backends](https://www.astronomer.io/guides/custom-xcom-backends) (eg. S3)
        - but you still need to pull data and use memory
        - or use references instead of actual data
- recomanded for passing small amounts of data
- before 2.0 XCOM serialization was done default by picling
- after 2.0 `enable_xcom_pickling = False` default serialization is JSON to avoid Remote Code Executions attacks
- can be seen in Admin/XCOMs

## TaskFlow API

- Decorators
    - Help you create dags easier
    - @task.python on top of your python function
    - @task.virtualenv
    - @task_group
    - @dag
    - just add decorators in front of the functions
- XCOM Args
    - automatically create explicit dependencies
    - returned params can be directly used and they will be passed through XCOMs
- the task name will be the function name
- the dag id will be the function name adnotated with @dag
- at the end you need to run the main function and store it in a variable
- for multiple xcom values
    - add multiple_outputs=True for multiple XCOMs - will also push dictionary
        - prevent push dictionary with do_xcom_push=False
    - or put  -> Dict[str, str] - with this doesn't seem to work for separate xcoms

## Group Tasks

- Subdags
    - pretty complicated, needs some specific associations
    - behind the scene it is a Sensor in Airflow 2.0, so it waits for the tasks to complete
        - can use poke_interval
        - can use mode='reschedule'
    - have to put task_concurrency within each task in subdag
- Tasks Groups
    - easy to use
    - can import a task group from other file
