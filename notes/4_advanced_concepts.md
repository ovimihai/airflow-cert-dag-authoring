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
        \-> x3 ->x5/

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
(1)  [A fail] -> [B] -> [C]
(2)  [A] -> [B] -> [C]
- case1: if A depends_on_past on A => (2)[A] will not be triggered

(1)  [A] -> [B fail] -> [C]
(2)  [A] -> [B] -> [C]

- case2: if B depends_on_past on B => (2)[B] will not be triggered, but (2)[A] will be triggered

- case3: if all depends_on_past on B => (2)[B] will not be triggered, but (2)[A] will be triggered