FROM quay.io/astronomer/ap-airflow:2.4.3-onbuild

ENV AIRFLOW_VAR_VARIABLE_NAME_1='{"key1":"value1", "key2":"value2", "my_dag_partner":"partner_name"}'
ENV AIRFLOW_VAR_MY_DAG_PARTNER='{"name":"partner name"}'

