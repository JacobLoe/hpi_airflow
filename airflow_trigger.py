import requests
import json
import argparse
import logging
from dateutil import parser


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
        dag_data = '{' + dag_data[1:-1] + ', "run_id":"{run_id}"'.format(run_id=run_id) + '}'

    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)
    response = requests.post(url, headers=headers, data=dag_data)

    # check whether the request was successful
    if response.status_code != int(200):
        print('response.status_code:', response.status_code)
        print('response.text: ', response.text)
        print('response.headers: ', response.headers)


def get_dag_info(dag_id, run_id, last_n):
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

    data = json.loads(response.content.decode('utf8'))
    # return the last n dag runs
    if last_n:
        data = data[-last_n:]
        return data
    # return a specific DAG run
    elif run_id:
        for k in data:
            if k['run_id'] == run_id:
                return k
    # return all DAG runs
    else:
        return data


def get_task_info(dag_id, task_id, run_id, last_n):
    # gives info about specific tasks, state, start/end-date for a specific run_id

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    if len(dag_id) > 1 and last_n and task_id and not run_id:
        # return the last n tasks
        # needs a list of all dag_ids and a list of all the tasks
        # then it runs get_task_info for each dag_id

        tasks = []
        for i, d in enumerate(dag_id):
            dags = get_dag_info(d, None, None)
            for j in dags:
                # ts.append([j['dag_id'], j['execution_date']])
                ed = j['execution_date']
                for t in task_id[i]:
                    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/{timestamp}/tasks/{task_id}'.format(dag_id=d, timestamp=ed, task_id=t)
                    response = requests.get(url, headers=headers)
                    r = json.loads(response.content.decode('utf8'))
                    try:
                        # convert the start_date to datetime object, to make it sortable
                        start_datetime = parser.parse(r['start_date'])
                        # add the converted time to the task dict instead of overwriting it
                        r['start_datetime'] = start_datetime
                        tasks.append(r)
                    except:
                        pass

        # sort the tasks by start_time and take last_n tasks that were started
        tasks = sorted(tasks, key=lambda k: k["start_datetime"], reverse=True)[:last_n]
        return tasks

    # elif dag_id and run_id and task_id and not last_n:
    #     # return the timestamp for a specific dag-run and specific task
    #
    #     # FIXME don't slice the list to get the timestamp
    #     timestamp = get_dag_info(dag_id, run_id, last_n)['execution_date'][:19]
    # elif dag_id and last_n and not task_id and not run_id:
    #     # return the last n tasks for a dag-run , regardless of the task and run id
    #     # needs to know which tasks are in a given dag
    #
    #     # FIXME don't slice the list to get the timestamp
    #     timestamp = get_dag_info(dag_id, run_id, last_n)
    #     timestamp = [t['execution_date'][:19] for t in timestamp]
    # elif dag_id and last_n and task_id and not run_id:
    #     # return the last n task_id tasks, regardless of the run_id
    #
    #     # FIXME don't slice the list to get the timestamp
    #     timestamp = get_dag_info(dag_id, run_id, last_n)
    #     timestamp = [t['execution_date'][:19] for t in timestamp]
    # elif dag_id and last_n and run_id and not task_id:
    #     # return the last_n tasks of the run_id dag
    #     pass
    # else:
    #     raise Exception('Something went wrong with the parameters')
    #
    # for ts in timestamp:
    #     url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/{timestamp}/tasks/{task_id}'.format(dag_id=dag_id, timestamp=ts, task_id=task_id)
    #     response = requests.get(url, headers=headers)
    #     # check whether the request was successful
    #     if response.status_code != int(200):
    #         print('response.status_code:', response.status_code)
    #         print('response.text: ', response.text)
    #         print('rsponse.headers: ', response.headers)
    #
    #     data = json.loads(response.content.decode('utf8'))
    #     print(data, '\n')


def get_dag_state(dag_id, run_id):
    # returns the state of a dag, either with a run_id or the last dag that was started
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    if run_id:
        return get_dag_info(dag_id, run_id, None)['state']
    else:
        dags = get_dag_info(dag_id, None, None)

        states = []
        for d in dags:
            sdt = parser.parse(d['start_date'])
            p = {'state': d['state'], 'start_datetime': sdt}
            states.append(p)

        state = sorted(states, key=lambda k: k["start_datetime"], reverse=True)[0]
        return state['state']


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

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('action', choices=('trigger', 'get_dag_info', 'get_task_info', 'get_dag_state'), help='decide the action that is send to the server')
    args_parser.add_argument('--dag_id', help='defines which DAG is targeted')
    args_parser.add_argument('--videoid', help='which video is supposed to be processed ,not functional, atm hardcoded to 6ffaf51')
    args_parser.add_argument('--task_id', help='specifies which task is looked at for info')
    args_parser.add_argument('--run_id', help='set the id of a dag run, has to be unique, if this is not used airflow uses an id with the format "manual__YYYY-mm-DDTHH:MM:SS"')
    args_parser.add_argument('--last_n', type=int, default=5, help='')
    args = args_parser.parse_args()

    dag_id = args.dag_id
    task_id = args.task_id
    run_id = args.run_id
    last_n = args.last_n

    if not dag_id:
        dag_id = ['shotdetection', 'feature_extraction']
        task_id_sd = ['push_config_to_xcom', 'get_video', 'shotdetection']
        task_id_fe = ['push_config_to_xcom', 'get_video', 'shotdetection', 'image_extraction', 'feature_extraction']
        task_id = [task_id_sd, task_id_fe]

    # FIXME hardcoded id just for testing
    videoid = args.videoid
    videoid = "6ffaf51" # downloads Occupy Wallstreet

    if args.action == 'trigger':
        with open('variables.json') as j:
            data = json.load(j)
            params = {key: data[key] for key in data}
        trigger_dag(dag_id, videoid, params, run_id)

    elif args.action == 'get_dag_info':
        for d in get_dag_info(dag_id, run_id, last_n):
            print(d, '\n')

    elif args.action == 'get_task_info':
        for d in get_task_info(dag_id, task_id, run_id, last_n):
            print(d, '\n')

    elif args.action == 'get_dag_state':
        print(get_dag_state(dag_id, run_id))

    else:
        raise Exception('action "{action}" could not be interpreted'.format(action=args.action))

