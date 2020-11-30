import requests
import json
import argparse


def trigger_dag(dag_id, videoid, dag_configuration, run_id):
    # triggers the DAG dag_id with the given dag_configuration_json

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    print('Starting DAG "{dag_id}" for id "{videoid}"'.format(dag_id=dag_id, videoid=videoid))
    # add the dag_id and the videoid to the dag_configuration_json
    dag_configuration['dag_id'] = dag_id
    dag_configuration['videoid'] = str(videoid)

    dag_configuration_json = json.dumps(dag_configuration)

    dag_data = '{"conf":'+dag_configuration_json+'}'

    # insert the run_id into the data for the DAG
    if run_id:
        dag_data = '{' + data[1:-1] + ', "run_id":"{run_id}"'.format(run_id=run_id) + '}'

    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)
    response = requests.post(url, headers=headers, data=dag_data)

    # check whether the request was successful
    if response.status_code != int(200):
        print('response.status_code:', response.status_code)
        print('response.text: ', response.text)
        print('response.headers: ', response.headers)


def get_dag_info(dag_id, run_id):
    # returns what graphs run at the moment and potential errors
    # info about all dag runs: dag_ids, execution_dates, state (running, failed, completed)
    # either for only the dag specified by the run_id or all dags that have run

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)   # info
    response = requests.get(url, headers=headers)

    # check whether the request was successful
    if response.status_code != int(200):
        print('response.status_code:', response.status_code)
        print('response.text: ', response.text)
        print('response.headers: ', response.headers)

    j = json.loads(response.content.decode('utf8'))
    # return a specific DAG run
    if run_id:
        for k in j:
            if k['run_id'] == run_id:
                print(k)
                return k
    # return all DAG runs
    else:
        for k in j:
            print(k, '\n')

    # # just gives same info (excluding the state) about the latest run and less than the first command, really useless
    # url = 'http://localhost:8080/api/experimental/latest_runs'
    # response = requests.get(url, headers=headers)
    # j = json.loads(response.content.decode('utf8'))
    # print(j)


def get_task_info(dag_id, task_id, run_id):
    # gives info about specific tasks, state, start/end-date for a specific run_id

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    # use the run_id to get the timestamp at which the dag was started, from which the task ran,
    if not run_id:
        raise Exception('missing run_id')
    timestamp = get_dag_info(dag_id, run_id)['execution_date'][:19]

    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/{timestamp}/tasks/{task_id}'.format(dag_id=dag_id, timestamp=timestamp, task_id=task_id)
    response = requests.get(url, headers=headers)
    # check whether the request was successful
    if response.status_code != int(200):
        print('response.status_code:', response.status_code)
        print('response.text: ', response.text)
        print('rsponse.headers: ', response.headers)

    j = json.loads(response.content.decode('utf8'))
    print('\ntask_info\n', j)


def pause_dag(dag_id):

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

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

    # # just returns the state of a dag at a specific timestamp
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/2020-11-30T20:45:01'.format(dag_id=dag_id)   # info
    # response = requests.get(url, headers=headers)
    # j = json.loads(response.content.decode('utf8'))
    # print('dag_runs')
    # print(j)
    # print('\n')

    # # info about a specific task, task parameters, kinda useless
    # # can return the command that was used for starting a container, but no the specific values
    # # for example returns: --sensitivity {{ti.xcom_pull(key="shotdetection_sensitivity", dag_id='+DAG_ID+')}
    # # instead of --sensitivity 60
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/tasks/{taskid}'.format(dag_id=dag_id, taskid=taskid)
    # response = requests.get(url, headers=headers)
    # j = json.loads(response.content.decode('utf8'))
    # print(j)
    # print('\n')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('action',choices=('trigger', 'get_dag_info', 'get_task_info') ,help='decide the action that is send to the server')
    parser.add_argument('dag_id', help='defines which DAG is targeted')
    parser.add_argument('--videoid', help='which video is supposed to be processed ,not functional, atm hardcoded to 6ffaf51')
    parser.add_argument('--task_id', help='specifies which task is looked at for info')
    parser.add_argument('--run_id', help='set the id of a dag run, has to be unique, if this is not used airflow uses an id with the format "manual__YYYY-mm-DDTHH:MM:SS"')
    args = parser.parse_args()

    dag_id = args.dag_id
    task_id = args.task_id
    run_id = args.run_id

    # FIXME hardcoded id just for testing
    videoid = args.videoid
    videoid = "6ffaf51" # downloads Occupy Wallstreet

    if args.action == 'trigger':
        with open('variables.json') as j:
            data = json.load(j)
            params = {key: data[key] for key in data}
        trigger_dag(dag_id, videoid, params, run_id)
    elif args.action == 'get_dag_info':
        get_dag_info(dag_id, run_id)
    elif args.action == 'get_task_info':
        get_task_info(dag_id, task_id, run_id)
    else:
        raise Exception('action "{action}" could not be interpreted'.format(action=args.action))

