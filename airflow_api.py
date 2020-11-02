# videoids = ['0, 25445a41b5bbda0ed7e2e0845eaa5c96373705c5c738fe640c1ea70a07b4176c']


dag_configuration = ''

a = 'curl -X POST http://localhost:8080/api/experimental/dags/hpi_extraction/dag_runs'
b = '-H "Cache-Control: no-cache" -H "Content-Type: application/json" '
c = '-d "{conf}"'.format(conf=dag_configuration)

