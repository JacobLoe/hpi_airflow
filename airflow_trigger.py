import requests
import json
import argparse
import logging
from dateutil import parser
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False    # prevent log messages from appearing twice


def trigger_dag(dag_id, videoid, dag_configuration, run_id):
    # triggers the DAG dag_id with the given dag_configuration_json

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    logger.info('Starting DAG "{dag_id}" for id "{videoid}"'.format(dag_id=dag_id, videoid=videoid))
    # add the dag_id and the videoid to the dag_configuration_json
    dag_configuration['dag_id'] = dag_id
    dag_configuration['videoid'] = str(videoid)

    dag_configuration_json = json.dumps(dag_configuration)

    dag_data = '{"conf":'+dag_configuration_json+'}'

    # insert the run_id into the data for the DAG
    if run_id:
        dag_data = '{' + dag_data[1:-1] + ', "run_id":"{run_id}"'.format(run_id=run_id) + '}'
    else:
        raise Exception('run_id missing')

    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)
    response = requests.post(url, headers=headers, data=dag_data)

    # check whether the request was successful
    if response.status_code != int(200):
        logger.info('response.status_code:', response.status_code)
        logger.info('response.text: ', response.text)
        logger.info('response.headers: ', response.headers)


def get_dag_info(dag_id, run_id, last_n):
    # returns what graphs run at the moment
    # info about all dag runs: dag_ids, execution_dates, state (running, failed, completed)
    # either for only the dag specified by the run_id or all dags that have run

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    if last_n and type(dag_id) != list:
        # return the last n runs, for a specific dag_id
        url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)  # info
        response = requests.get(url, headers=headers)

        # check whether the request was successful
        if response.status_code != int(200):
            logger.info('response.status_code:', response.status_code)
            logger.info('response.text: ', response.text)
            logger.info('response.headers: ', response.headers)

        data = json.loads(response.content.decode('utf8'))

        data = data[-last_n:]
        return data

    elif run_id and type(dag_id) != list:
        # return a specific DAG run, identfied by its run_id
        # FIXME make this work without specifying a dag_id
        url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)  # info
        response = requests.get(url, headers=headers)

        # check whether the request was successful
        if response.status_code != int(200):
            logger.info('response.status_code:', response.status_code)
            logger.info('response.text: ', response.text)
            logger.info('response.headers: ', response.headers)

        data = json.loads(response.content.decode('utf8'))

        for k in data:
            if k['run_id'] == run_id:
                return k
    elif type(dag_id) != list:
        # return all DAG runs for a specific dag_id
        url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)  # info
        response = requests.get(url, headers=headers)

        # check whether the request was successful
        if response.status_code != int(200):
            logger.info('response.status_code:', response.status_code)
            logger.info('response.text: ', response.text)
            logger.info('response.headers: ', response.headers)

        data = json.loads(response.content.decode('utf8'))

        return data
    elif type(dag_id) == list and last_n:
        # return info for all the dags regardless of dag_id, either all or the last n than have run
        d = []
        for di in dag_id:
            info = get_dag_info(dag_id=di, run_id=None, last_n=last_n)
            for i in info:
                start_date = str(parser.parse(i['start_date']))
                i['start_date'] = start_date
                d.append(i)

        # sort the dags by start_time and take the last_n dags that were started
        dags = sorted(d, key=lambda k: k["start_date"], reverse=True)[:last_n]
        return dags
    elif type(dag_id) == list and not last_n:
        d = []
        for di in dag_id:
            info = get_dag_info(dag_id=di, run_id=None, last_n=None)
            for i in info:
                # convert the start date to a sortable type
                start_date = str(parser.parse(i['start_date']))
                i['start_date'] = start_date
                d.append(i)

        # sort the dags by start_time and take the last_n dags that were started
        dags = sorted(d, key=lambda k: k["start_date"], reverse=True)
        return dags


def get_task_info(dag_id, task_id, run_id, last_n):
    # gives info about specific tasks, state, start/end-date for a specific run_id

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    if type(dag_id) == list and last_n and task_id and not run_id:
        # return the last n tasks
        # needs a list of all dag_ids and a list of all the tasks
        # then it runs get_task_info for each dag_id

        tasks = []
        for i, di in enumerate(dag_id):
            dags = get_dag_info(dag_id=di, run_id=None, last_n=last_n)
            for d in dags:
                ed = d['execution_date']
                for ti in task_id[i]:
                    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/{timestamp}/tasks/{task_id}'.format(dag_id=di, timestamp=ed, task_id=ti)
                    response = requests.get(url, headers=headers)
                    r = json.loads(response.content.decode('utf8'))
                    try:
                        # convert the start_date to datetime object, to make it sortable
                        start_date = str(parser.parse(r['start_date']))
                        r['start_date'] = start_date
                        tasks.append(r)
                    except:
                        # if the try block didn't work the the task was not started yet
                        # this either due to failure of the previous task
                        # or the previous task is not finished yet
                        break

        # sort the tasks by start_time and take last_n tasks that were started
        tasks = sorted(tasks, key=lambda k: k["start_date"], reverse=True)[:last_n]
        return tasks

    if type(dag_id) == list and task_id and not last_n and not run_id:
        # return all tasks
        # needs a list of all dag_ids and a list of all the tasks
        # then it runs get_task_info for each dag_id

        tasks = []
        for i, di in enumerate(dag_id):
            dags = get_dag_info(dag_id=di, run_id=None, last_n=last_n)
            for d in dags:
                ed = d['execution_date']
                for ti in task_id[i]:
                    url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/{timestamp}/tasks/{task_id}'.format(dag_id=di, timestamp=ed, task_id=ti)
                    response = requests.get(url, headers=headers)
                    r = json.loads(response.content.decode('utf8'))
                    try:
                        # convert the start_date to datetime object, to make it sortable
                        start_date = str(parser.parse(r['start_date']))
                        r['start_date'] = start_date
                        tasks.append(r)
                    except:
                        # if the try block didn't work the the task was not started yet
                        # this either due to failure of the previous task
                        # or the previous task is not finished yet
                        break

        # sort the tasks by start_time and take last_n tasks that were started
        tasks = sorted(tasks, key=lambda k: k["start_date"], reverse=True)
        return tasks

    elif dag_id and run_id and task_id and not last_n:
        # return info for a specific task
        # FIXME maybe don't slice the list to get the correct timestamp
        timestamp = [get_dag_info(dag_id, run_id, last_n)['execution_date'][:19]]

    elif dag_id and last_n and type(task_id) == dict and not run_id:
        # return the last n tasks for a dag-run , regardless of the task and run id
        # needs to know which tasks are in a given dag

        # get the excecution date for of each dag_id dag
        dags = get_dag_info(dag_id=dag_id, run_id=None, last_n=last_n)

        tasks = []
        for d in dags:
            ed = d['execution_date']
            for ti in task_id[dag_id]:
                url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/{timestamp}/tasks/{task_id}'.format(dag_id=dag_id, timestamp=ed, task_id=ti)
                response = requests.get(url, headers=headers)
                r = json.loads(response.content.decode('utf8'))
                try:
                    # convert the start_date to datetime object, to make it sortable
                    start_date = str(parser.parse(r['start_date']))
                    r['start_date'] = start_date
                    tasks.append(r)
                except:
                    # if the try block didn't work the the task was not started yet
                    # this either due to failure of the previous task
                    # or the previous task is not finished yet
                    break

        # sort the tasks by start_time and take the last_n tasks that were started
        tasks = sorted(tasks, key=lambda k: k["start_date"], reverse=True)[:last_n]
        return tasks

    elif dag_id and last_n and task_id and not run_id:
        # return the last n task_id tasks, regardless of the run_id

        # get the excecution date for of each dag_id dag
        dags = get_dag_info(dag_id=dag_id, run_id=None, last_n=last_n)

        tasks = []
        for d in dags:
            ed = d['execution_date']
            url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/{timestamp}/tasks/{task_id}'.format(dag_id=dag_id, timestamp=ed, task_id=task_id)
            response = requests.get(url, headers=headers)
            r = json.loads(response.content.decode('utf8'))
            try:
                # convert the start_date to datetime object, to make it sortable
                start_date = str(parser.parse(r['start_date']))
                r['start_date'] = start_date
                tasks.append(r)
            except:
                # if the try block didn't work the the task was not started yet
                # this either due to failure of the previous task
                # or the previous task is not finished yet
                break

        # sort the tasks by start_time and take last_n tasks that were started
        tasks = sorted(tasks, key=lambda k: k["start_date"], reverse=True)[:last_n]
        return tasks

    elif dag_id and last_n and run_id and type(task_id) == dict:
        # return the last_n tasks of the run_id dag
        # get the excecution date for of each dag_id dag
        dags = get_dag_info(dag_id=dag_id, run_id=run_id, last_n=None)

        tasks = []
        ed = dags['execution_date']
        for ti in task_id[dag_id]:
            url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/{timestamp}/tasks/{task_id}'.format(dag_id=dag_id, timestamp=ed, task_id=ti)
            response = requests.get(url, headers=headers)
            r = json.loads(response.content.decode('utf8'))
            try:
                # convert the start_date to datetime object, to make it sortable
                start_date = str(parser.parse(r['start_date']))
                r['start_date'] = start_date
                tasks.append(r)
            except:
                # if the try block didn't work the the task was not started yet
                # this either due to failure of the previous task
                # or the previous task is not finished yet
                break

        # sort the tasks by start_time and take last_n tasks that were started
        tasks = sorted(tasks, key=lambda k: k["start_date"], reverse=True)[:last_n]
        return tasks

    else:
        return 'Something went wrong with the parameters'

    data = []
    for ts in timestamp:
        url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs/{timestamp}/tasks/{task_id}'.format(dag_id=dag_id, timestamp=ts, task_id=task_id)
        response = requests.get(url, headers=headers)
        # check whether the request was successful
        if response.status_code != int(200):
            logger.info('response.status_code:', response.status_code)
            logger.info('response.text: ', response.text)
            logger.info('response.headers: ', response.headers)

        data.append(json.loads(response.content.decode('utf8')))

    return data


def get_dag_state(dag_id, run_id):
    # returns the state of a dag, either with a run_id or the last dag that was started

    if run_id:
        return get_dag_info(dag_id, run_id, None)['state']
    elif type(dag_id) == list:
        states = []
        for di in dag_id:
            dags = get_dag_info(di, None, None)
            for d in dags:
                star_date = parser.parse(d['start_date'])
                p = {'state': d['state'], 'start_date': star_date, 'dag_id':d['dag_id']}
                states.append(p)
        state = sorted(states, key=lambda k: k["start_date"], reverse=True)[0]
        return state['dag_id'], state['state']


def get_task_logs(logs_folder, dag_id, task_id, run_id):
    # returns the log-file for a specific task, based on the execution_data of their dag

    log_path = os.path.join(logs_folder, dag_id, task_id, '2020-12-14T21:50:40+00:00', '1.log')
    with open(log_path) as l:
        log = l.read()
    return log


if __name__ == '__main__':

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('action', choices=('trigger', 'get_dag_info', 'get_task_info', 'get_dag_state', 'get_task_logs'), help='decide the action that is send to the server')
    args_parser.add_argument('--dag_id', choices=('shotdetection', 'feature_extraction', 'aspect_ratio_extraction', 'optical_flow'), help='defines which DAG is targeted')
    args_parser.add_argument('--videoid', help='which video is supposed to be processed ,not functional, atm hardcoded to 6ffaf51')
    args_parser.add_argument('--task_id', help='specifies which task is looked at for info')
    args_parser.add_argument('--run_id', help='set the id of a dag run, has to be unique, if this is not used airflow uses an id with the format "manual__YYYY-mm-DDTHH:MM:SS"')
    args_parser.add_argument('--last_n', type=int, help='returns the last n infos of either tasks or dags')
    args = args_parser.parse_args()

    dag_id = args.dag_id
    task_id = args.task_id
    run_id = args.run_id
    last_n = args.last_n
    # FIXME hardcoded id just for testing
    videoid = args.videoid
    # videoid = "6ffaf51"     # downloads Occupy Wallstreet

    # these
    if not dag_id:
        dag_id = ['shotdetection', 'feature_extraction', 'aspect_ratio_extraction', 'optical_flow']
        task_id_sd = ['push_config_to_xcom', 'get_video', 'shotdetection']
        task_id_fe = ['push_config_to_xcom', 'get_video', 'shotdetection', 'image_extraction', 'feature_extraction', 'update_index']
        task_id_ae = ['push_config_to_xcom', 'get_video', 'shotdetection', 'image_extraction', 'aspect_ratio_extraction']
        task_id_of = ['push_config_to_xcom', 'get_video', 'optical_flow']
        task_id = [task_id_sd, task_id_fe, task_id_ae, task_id_of]
    if dag_id and last_n and not task_id and not run_id:
        task_id_sd = ['push_config_to_xcom', 'get_video', 'shotdetection']
        task_id_fe = ['push_config_to_xcom', 'get_video', 'shotdetection', 'image_extraction', 'feature_extraction', 'update_index']
        task_id_ae = ['push_config_to_xcom', 'get_video', 'shotdetection', 'image_extraction', 'aspect_ratio_extraction']
        task_id_of = ['push_config_to_xcom', 'get_video', 'optical_flow']
        task_id = {'shotdetection': task_id_sd, 'feature_extraction': task_id_fe, 'aspect_ratio_extraction': task_id_ae, 'optical_flow': task_id_of}
    if dag_id and last_n and run_id and not task_id:
        task_id_sd = ['push_config_to_xcom', 'get_video', 'shotdetection']
        task_id_fe = ['push_config_to_xcom', 'get_video', 'shotdetection', 'image_extraction', 'feature_extraction', 'update_index']
        task_id_ae = ['push_config_to_xcom', 'get_video', 'shotdetection', 'image_extraction', 'aspect_ratio_extraction']
        task_id_of = ['push_config_to_xcom', 'get_video', 'optical_flow']
        task_id = {'shotdetection': task_id_sd, 'feature_extraction': task_id_fe, 'aspect_ratio_extraction': task_id_ae, 'optical_flow': task_id_of}

    if args.action == 'trigger':
        with open('config.json') as j:
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

    elif args.action == 'get_task_logs':
        print(get_task_logs('../static/data/airflow/logs', 'optical_flow', 'get_video', 'test1'))

    else:
        raise Exception('action "{action}" could not be interpreted'.format(action=args.action))

