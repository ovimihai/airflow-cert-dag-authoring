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
- limitations:
    - 