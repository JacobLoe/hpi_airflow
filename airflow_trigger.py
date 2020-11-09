import requests
import json


def trigger_dag(dag_id, dag_configuration_json):
    # triggers the DAG dag_id with the given dag_configuration_json
    dag_id = 'shotdetection'

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    # FIXME don't read the confiration from disk, but get it from a server/client
    with open('variables.json') as j:
        data = json.load(j)
        params = {key: data[key] for key in data}

    params['DAG_ID'] = dag_id
    params['videoid'] = '0'
    dag_configuration_json = json.dumps(params)

    data = '{"conf":'+dag_configuration_json+'}'

    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)
    response = requests.post(url, headers=headers, data=data)
    print(response)


if __name__ == '__main__':
    trigger_dag(0, 0)
