# Advanced concepts

## Dynamic tasks
- can create dynamic tasks only if Airflow knows the parameters beforehand
- can't create tasks pased on other tasks output
- can create tasks based on a dictionary or a variable or even on some connection in the database

## Branching

- BranchPythonOperator, BranchSqlOperator, BranchDateTimeOperator, BranchDayOfWeekOperator
- you always need to return a task_id
- for missing days, you could use a Dummy Operator
- for skiped tasks with one parent that ran you can use trigger_rule='none_failed_or_skipped' to prevent skip

**Trigger Rules**
- all_success - triggered if all parents succeded
- all_failed - triggered if all parents failed (eg. email notification)
- all_done - all of the parents is done, no matter if they failed or succeded
- one_failed - as soon as one parent failed
- one_success - as soon as one parent success
- none_failed - run if no parent task failed or has the status upstream_failed (one of its parents failed)
- none_skiped - run if none of the parents were skipped
- none_failed_or_skipped - trigger if at lease one one of the parents succeded and all of the parents is done
- dummy - your task gets trigger imediatly

## Dependencies and Helpers
- old way: set_upstream, set_downstream
- new way with bitshift operators: t1 << t2,  t1 >> t2
- [t1, t2, t3] >> t5 - OK
- [t1, t2, t3] >> [t4, t5, t6] - it doesn't work; error: you can't trade dependencies between two lists
- cross dependencies
    - v1:
        t1 >> t4
        t2 >> t4
        t3 >> t4
        ...
    - v2
        [t1, t2, t3] >> t4
        [t1, t2, t3] >> t5
        ...
    - v3 ok
        from airflow.models.baseoperator import cross_downstream
        cross_downstream([t1, t2, t3], [t4, t5, t6])
        cross_downstream doesn't return, so you cant continue directly the dependencies
- chain
    - from airflow.models.baseoperator import chain
    - chain(x1, [x2,x3], [x4,x5], x6)
    - x1 -> x2 ->x4 ->x6
    -     \-> x3 ->x5/

## Configuration

Global
- PARALLELISM = 32 - tasks executed in parallel for the entire Airflow instance
- DAG_CONCURRENCY = 16 - number of tasks that can run at the same for a specific dag
- MAX_ACTIVE_RUNS_PER_DAG = 16 - dag_runs that can run at the same time for a given tag

At DAG level
- concurrency = 2 - two tasks running at the same for all dag_runs
- max_active_runs = 2 - run only 2 dags at a time for a specific dag

At Task level
- task_concurrency = 1 - only one task running at the same time for all dag_runs
- pool = 'default_pool'

## Pools

- define worker slots
- default_pool with 128 slots
    - running slots - active
    - queued slots - waiting
- can create a pool in the interface
- can be applied at the DAG or Tasks level
- pool_slots - the number of slots a given task will take
- for pool set at the SubDags level will not be respected by the subdag tasks, it will be used only by the SubDag itself

## Tasks priority

- priority_weight at task level
- bigger weights are ran first
- you probably need a smaller pool to see the effect
- manually triggered dags don't respect priorities
- weight_rule
    - downstream - add up downstream
    - upstream - add up on the upstream
    - absolute - based on the priority rules you define
- to prioritize a dag against another
    - define a higher (99) priority for all dags tasks

**Depends on past**
- (1)  [A fail] -> [B] -> [C]
- (2)  [A] -> [B] -> [C]
- case1: if A depends_on_past on A => (2)[A] will not be triggered

- (1)  [A] -> [B fail] -> [C]
- (2)  [A] -> [B] -> [C]
- case2: if B depends_on_past on B => (2)[B] will not be triggered, but (2)[A] will be triggered

- if the tasks will not be triggered will have no status 
    - it is recomanded to always have a timeout on dags otherwise will run forever
- for the first run, depends_on_past is ignored
- for backfills it is also ignored
- the tasks are triggered iven if the past task was skipped

**Wait for downstream** - commonly used with depends on past
- (1)  [A] -> [B] -> [C]
- (2)  [A] -> [B] -> [C]

- if wait for downstream is True
    - (2)[A] will run only if (1)[A] and (1)[B] succeded - only waiting for the direct downstream
- if you set this parameter, the depends_on_past will be automatically set to True
- might be usefull when changing the same resources, to avoid race conditions

## Sensors
[docs](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/sensors/index.html)
- an Operator that waits for a condition to be true before moving to the next task
- eg. FileSensor, DateTimeSensor, SqlSensor
- for DateTimeSensor meaningfull arguments
    - target_time - timedalta, can be templated
    - poke_interval - the time it will retry
    - mode
        - poke every poke_interval - will block a worker slot
        - reschedule - will not block a worker set
    - timeout = 7days - this default value can ba bad - available for Sensors
        - you should define a better suited timeout
        - used with soft_fail=True - will skip the task on timeout
    - execution_timeout - this doesn't have a default value - available for all Operators
    - exponential_backoff=True - will increase exponentially the waiting period
- ! always define a timeout

## Timeouts
- can be defined at the DAG level with - dagrun_timeout
- always recomanded to avoid having too many dags running indefinitely
- works only for scheduled dags - for manually triggederd dags will not be used
- at the Operator level you can use execution_level
    - doesn't have a value by default
    - also should always define a timeout

## Mange failures
- at the DAG level
    - on_success_callback(context)
    - on_failure_callback
        - here you can send a notification
        - if you have a failure in your fallback, the callback will not be retried
- at the Task level
    - on_success_callback
    - on_failure_callback
    - on_retry_callback
        - can you do something between each retries
    - if it failed due to an timeout or an error
        - context['exception'] will be an instance of some exception (import airflow.exceptions)
            - AirflowTaskTimeout
            - AirflowSensorTimeout
            - ...
    - context['ti'].try_number() - will give you the retry number

## Different ways to retry
- `default_task_retries` (config) - overriden by `retries` at DAG - overriden by `retries` Task level
- `retry_delay` timedelta(minutes=5) default
- `retry_exponential_backoff` - will wait more on each retry
    - usefull when you fetch from an API or a Database
- `max_retry_delay` timedelta - limit the exponential_backoff

## SLA
- receive a notification when a task takes too much, but less than the timeout
- at the Task level
    - `sla` timedelta
        - related to the dag execution_date not to the task start_time
        - ! if you have a long task before the sla will be missed
        - if you want sla of 10min for the DAG - define a SLA for the `last task` of 10min
    - `on_sla_miss_callback` at the DAG level
        - callback(dag, task_list, blocking_task_list, slas, blocking_tis)
            - blocking_tis - blocking_task_list - t1 >> t2 - if both fail sla - the t1 will be blocking t2
            - slas - tasks_list - list of all tasks that missed their slas
    - manually triggered Tasks will not have SLAs
    - you need to configure smtp settings to get notified by mail

## DAG versioning
- there is no real mechanism to deal with this - it is comming in the future
- new tasks will have `no status` for the previous dag_runs
    - for a queued task - the new version will not be taken into conideration
- for a removed task - all previous runs will not be showing any more
- be verry carefull when
    - remove a task
    - a task is running during an update
- best practice 
    - add version suffix _1_0_0

## Dynamically generating DAGs
- Single File method
    - for loop with globals()[dag_id]
    - dags will be generated every time the Scheduler will parse the DAGs folder
    - there will be performance issues
    - you can't see the actual dag code in the UI
    - if you change the number of dags generated they will not be shown any more in the UI
- Multi File method
    - use template files
    - generate actual files somewhere else - eg. CI/CD pipeline
    - obviously this taks more work
    - pros
        - scalable
        - one DAG one file
        - less prone to errors or zombie DAGs

