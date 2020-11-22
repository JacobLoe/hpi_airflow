import requests
import json


def trigger_dag(dag_id, videoid, dag_configuration, headers):
    # triggers the DAG dag_id with the given dag_configuration_json
    # add the dag_id and the videoid to the dag_configuration_json

    dag_configuration['DAG_ID'] = dag_id
    dag_configuration['videoid'] = str(videoid)

    dag_configuration_json = json.dumps(dag_configuration)

    data = '{"conf":'+dag_configuration_json+'}'

    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)
    response = requests.post(url, headers=headers, data=data)
    print(response)
    print(response.content)


def get_dag_status(dag_id, headers):
    # returns what graphs run at the moment and potential errors

    # info about all dag runs: dag_ids, execution_dates, state
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)   # info
    # info about a specific task, parameters
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/tasks/shotdetection'.format(dag_id=dag_id)
    # just gives info about the latest runs and less than the first command
    # url = 'http://localhost:8080/api/experimental/latest_runs'
    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/2020-11-17T09:35:29/tasks/get_videos'.format(dag_id=dag_id)
    response = requests.get(url, headers=headers)
    print('type response: ', type(response.content))
    p = response.content.decode('utf8')
    o = json.loads(p)
    print(o)


def get_queue():
    # returns which DAGs are currently running and which are scheduled to run
    pass


def pause_dag(dag_id, headers):

    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/paused/true'.format(dag_id=dag_id)
    response = requests.post(url, headers=headers)
    print('paused: ', response.content)


if __name__ == '__main__':

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    dag_id = 'shotdetection'
    # FIXME hardcoded id just for testing
    videoid = "6ffaf51" #Occupy Wallstreet

    with open('variables.json') as j:
        data = json.load(j)
        params = {key: data[key] for key in data}

    # pause_dag(dag_id, headers)
    trigger_dag(dag_id, videoid, params, headers)
    # get_dag_status(dag_id, headers)

