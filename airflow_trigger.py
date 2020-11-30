import requests
import json


def trigger_dag(dag_id, videoid, dag_configuration, headers):
    # triggers the DAG dag_id with the given dag_configuration_json
    # add the dag_id and the videoid to the dag_configuration_json

    dag_configuration['dag_id'] = dag_id
    dag_configuration['videoid'] = str(videoid)

    dag_configuration_json = json.dumps(dag_configuration)

    data = '{"conf":'+dag_configuration_json+'}'

    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)
    response = requests.post(url, headers=headers, data=data)
    print(response)
    print(response.content)


def get_dag_status(dag_id, headers):
    # returns what graphs run at the moment and potential errors
    taskid = 'shotdetection'
    # info about all dag runs: dag_ids, execution_dates, state (running, failed, completed)
    # dags are identified
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)   # info
    # response = requests.get(url, headers=headers)
    # j = json.loads(response.content.decode('utf8'))
    # print('dag_runs')
    # for k in j:
    #     print(k)
    # print('\n')
    # info about a specific task, task parameters, kinda useless
    # can return the command that was used for starting a container, but no the specific values
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/tasks/{taskid}'.format(dag_id=dag_id, taskid=taskid)
    # response = requests.get(url, headers=headers)
    # j = json.loads(response.content.decode('utf8'))
    # print(j)
    # print('\n')
    # just gives same info (excluding the state) about the latest run and less than the first command, really useless
    # url = 'http://localhost:8080/api/experimental/latest_runs'
    # response = requests.get(url, headers=headers)
    # j = json.loads(response.content.decode('utf8'))
    # print(j)
    # print('\n')
    # gives info about specific tasks, state, start/end-date
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/2020-11-23T20:54:24/tasks/push_config_to_xcom'.format(dag_id=dag_id)
    # response = requests.get(url, headers=headers)
    # j = json.loads(response.content.decode('utf8'))
    # print(j, '\n')
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/2020-11-23T20:54:24/tasks/get_video'.format(dag_id=dag_id)
    # response = requests.get(url, headers=headers)
    # j = json.loads(response.content.decode('utf8'))
    # print(j, '\n')
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/2020-11-23T20:54:24/tasks/{taskid}'.format(dag_id=dag_id, taskid=taskid)
    # response = requests.get(url, headers=headers)
    # j = json.loads(response.content.decode('utf8'))
    # print(j, '\n')
    # just returns the state
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/2020-11-23T20:54:24'.format(dag_id=dag_id)   # info
    # response = requests.get(url, headers=headers)
    # j = json.loads(response.content.decode('utf8'))
    # print('dag_runs')
    # print(j)
    # print('\n')


def pause_dag(dag_id, headers):

    # returns whether a dag is paused
    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/paused'.format(dag_id=dag_id)   # info
    response = requests.get(url, headers=headers)
    j = json.loads(response.content.decode('utf8'))
    print('dag_runs')
    print(j)
    print('\n')
    # pauses a dag, paused dags still accept triggers but won't exceute them until unpaused, while paused the dag state is freezed
    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/paused/true'.format(dag_id=dag_id)   # info
    response = requests.get(url, headers=headers)
    j = json.loads(response.content.decode('utf8'))
    print('dag_runs')
    print(j)
    print('\n')


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

