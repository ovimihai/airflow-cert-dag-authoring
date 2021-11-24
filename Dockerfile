FROM quay.io/astronomer/ap-airflow:2.2.1-buster-onbuild

ENV AIRFLOW_VAR_VARIABLE_NAME_1='{"key1":"value1", "key2":"value2"}'

