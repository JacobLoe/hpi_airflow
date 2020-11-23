from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from docker_operator import DockerOperator
from airflow.utils.dates import days_ago
from get_video import get_video

#
DAG_ID = 'shotdetection'

# default arguments inherited by each task
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'provide_context': True,    # is needed for tasks to communicate via xcom
}


def push_config_to_xcom(**context):
    # gets all relevant extractor parameters from the dag configuration and and pushes them to xcom
    # this function should only be called once

    videoid = context['dag_run'].conf['videoid']
    volumes_data_path = context['dag_run'].conf['volumes_data_path']
    extractor_file_extension = context['dag_run'].conf['extractor_file_extension']

    shotdetection_sensitivity = context['dag_run'].conf['shotdetection_sensitivity']
    shotdetection_force_run = context['dag_run'].conf['shotdetection_force_run']

    # xcoms are automatically mapped to the task_id and dag_id in which the created to prevent an incorrect pull
    context['ti'].xcom_push(key='videoid', value=videoid)
    context['ti'].xcom_push(key='volumes_data_path', value=volumes_data_path)
    context['ti'].xcom_push(key='extractor_file_extension', value=extractor_file_extension)

    context['ti'].xcom_push(key='shotdetection_sensitivity', value=shotdetection_sensitivity)
    context['ti'].xcom_push(key='shotdetection_force_run', value=shotdetection_force_run)


with DAG(DAG_ID, default_args=default_args,
         schedule_interval=None,
         max_active_runs=1,  # prevents more than one graph from running at a time
         concurrency=1) as dag:

    task_push_config_to_xcom = PythonOperator(
        task_id='push_config_to_xcom',
        python_callable=push_config_to_xcom
    )

    task_get_video = PythonOperator(
        task_id='get_video',
        python_callable=get_video
    )

    task_shotdetection = (DockerOperator(
        task_id='shotdetection',
        image='jacobloe/shot_detection:0.6',
        command='/data {{ti.xcom_pull(key="video_checksum", dag_id='+DAG_ID+')}}'
                ' --sensitivity {{ti.xcom_pull(key="shotdetection_sensitivity", dag_id='+DAG_ID+')}}'
                ' --force_run {{ti.xcom_pull(key="shotdetection_force_run", dag_id='+DAG_ID+')}}',
        volumes=['{{ti.xcom_pull(key="volumes_data_path", dag_id='+DAG_ID+')}}',
                 '/var/run/docker.sock:/var/run/docker.sock'],
        xcom_all=True,
    ))
    task_push_config_to_xcom >> task_get_video >> task_shotdetection
