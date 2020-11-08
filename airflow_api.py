from airflow.api.client.local_client import Client

videoids = ['0, 25445a41b5bbda0ed7e2e0845eaa5c96373705c5c738fe640c1ea70a07b4176c']

c = Client(None, None)
# run_id has to different for every run
c.trigger_dag(dag_id='hpi_extraction', run_id='hpi1', conf={})