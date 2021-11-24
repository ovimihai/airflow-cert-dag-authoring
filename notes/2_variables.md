# Variables

Create in Airflow UI - Admin -> Variables `/variable/add`
- key, val, description
    - prefix key with dag name to know where is used

```python
from airflow.models import Variable

Variable.get("my_variable") # this is read very often
```
- will create a connection to the metadata database

## Properly fetch your Variables
- min_file_processing_intervals - will fetch the variable every x seconds
- if you use the `Variable.get` outside dags or callbacks - they will be read from the metadata database every time the scheduler reads the files
- use JSON values for multiple variables - with only one connection
    - val: {"key1":"value1", "key2":"value2"}
    - my_var = Variable.get("my_variable", deserialize_json=True)
    - my_var['key1']
- fetch in params with templating:
    `op_args=["{{ var.json.my_variable.key1 }}"]`

## The Power of Environment Variables

In the Dockerfile
```Docker
ENV AIRFLOW_VAR_VARIABLE_NAME_1='{"key1":"value1", "key2":"value2"}'
```
- !!! this variables will be hidden from the users and will not connect or be stored in the metadata database

There are 6 ways to create variables
- Airflow UI
- Airflow CLI
- REST API
- Environment Variables
    - avoid connections to the DB
    - hide sensitive values in the UI
- [Secret Backend](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/secrets-backend/index.html) - local files or custom backends (Vault)
- Programatically

The order that Airflow checks for variables:
Secrets Backends -> Environment variable -> DB

Can also create connections like this
AIRFLOW_CONN_NAME_OF_CONNECTION=your_connection
