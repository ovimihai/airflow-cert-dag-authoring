# DAG dependencies

## ExternalTaskSensor

- dags should have the same execution date
- arguments
    - external_dag_id
    - external_task_id
    - execution_delta - use if the execution_times are different
    - execution_delta_fn - for more compelx cases
    - failed_states - a list of statuses eg. ['failed', 'skipped']
    - alowd_states - eg. ['success']
- external sensor fails by default after 7 days
- if the task you are waiting for fails, the sensor task will wait until timeout

## TriggerDagRunOperator
- this can be a bettery way than the external Sensor
- arguments
    - trigger_dag_id
    - execution_date (string|timedelta) - eg. "{{ ds }}"
    - wait_for_completion - wait for the triggered dag to finish
        - poke_interval
        - mode is not available!
    - reset_dag_run
        - if you clear the parent without this set to True, the triggered dag will raise an exception
        - you can't trigger a dag with the same execution_date twice without this
        - also can't backfill without this
    - failed_states - use if you wait

    


Notices
- XCOMs are not removed autmatically
