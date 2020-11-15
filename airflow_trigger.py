import requests
import json


def trigger_dag(dag_id, videoid, dag_configuration_json):
    # triggers the DAG dag_id with the given dag_configuration_json
    dag_id = 'shotdetection'
    # FIXME hardcoded id just for testing
    videoid = "6ffaf51" #Occupy Wallstreet

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    # FIXME don't read the confiration from disk, but get it from a server/client
    # add the dag_id and the videoid to the dag_configuration_json
    with open('variables.json') as j:
        data = json.load(j)
        params = {key: data[key] for key in data}
    params['DAG_ID'] = dag_id
    params['videoid'] = str(videoid)
    dag_configuration_json = json.dumps(params)

    data = '{"conf":'+dag_configuration_json+'}'

    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)
    response = requests.post(url, headers=headers, data=data)


def get_dag_status():
    # returns what graphs run at the momen and potential erros
    pass


def get_queue():
    # returns which DAGs are currently running nad which are scheduled to run
    pass


if __name__ == '__main__':
    trigger_dag(0, 0, 0)
