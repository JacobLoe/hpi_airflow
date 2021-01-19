from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from docker_operator import DockerOperator
from airflow.utils.dates import days_ago
from get_video import get_video
import requests
import os

DAG_ID = 'feature_extraction'

if 'IMAGESEARCH_HOST' in os.environ:
    IMAGESEARCH_HOST = os.environ['IMAGESEARCH_HOST']
else:
    IMAGESEARCH_HOST = 'server_ndd'

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
    get_video_force_run = context['dag_run'].conf['get_video_force_run']

    shotdetection_sensitivity = context['dag_run'].conf['shotdetection_sensitivity']
    shotdetection_force_run = context['dag_run'].conf['shotdetection_force_run']

    image_extraction_trim_frames = context['dag_run'].conf['image_extraction_trim_frames']
    image_extraction_frame_width = context['dag_run'].conf['image_extraction_frame_width']
    image_extraction_force_run = context['dag_run'].conf['image_extraction_force_run']

    feature_extraction_force_run = context['dag_run'].conf['feature_extraction_force_run']

    # xcoms are automatically mapped to the task_id and dag_id in which the created to prevent an incorrect pull
    context['ti'].xcom_push(key='videoid', value=videoid)

    context['ti'].xcom_push(key='volumes_data_path', value=volumes_data_path)
    context['ti'].xcom_push(key='extractor_file_extension', value=extractor_file_extension)
    context['ti'].xcom_push(key='get_video_force_run', value=get_video_force_run)

    context['ti'].xcom_push(key='shotdetection_sensitivity', value=shotdetection_sensitivity)
    context['ti'].xcom_push(key='shotdetection_force_run', value=shotdetection_force_run)

    context['ti'].xcom_push(key='image_extraction_trim_frames', value=image_extraction_trim_frames)
    context['ti'].xcom_push(key='image_extraction_frame_width', value=image_extraction_frame_width)
    context['ti'].xcom_push(key='image_extraction_force_run', value=image_extraction_force_run)

    context['ti'].xcom_push(key='feature_extraction_force_run', value=feature_extraction_force_run)


def update_index(**context):
    # sends a request to the imagesearch server to update (or create) a feature index with the current movie
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    url = 'http://server_ndd:9000/'.format(hostname=IMAGESEARCH_HOST)
    force_run = context['ti'].xcom_pull(key='update_index_force_run', dag_id=DAG_ID)
    r = requests.post(url, headers=headers, json={
                        'update_index': True,
                        'force_run': force_run
                      })
    if r.status_code != 200:
        raise Exception('Could not update index')


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

    task_shotdetection = DockerOperator(
        task_id='shotdetection',
        image='jacobloe/shotdetect:0.7',
        command='/data {{ti.xcom_pull(key="video_checksum", dag_id='+DAG_ID+')}}'
                ' --sensitivity {{ti.xcom_pull(key="shotdetection_sensitivity", dag_id='+DAG_ID+')}}'
                ' --force_run {{ti.xcom_pull(key="shotdetection_force_run", dag_id='+DAG_ID+')}}',
        volumes=['{{ti.xcom_pull(key="volumes_data_path", dag_id='+DAG_ID+')}}'],
        xcom_all=True,
    )

    task_image_extraction = DockerOperator(
        task_id='image_extraction',
        image='jacobloe/extract_images:0.7',
        command='/data {{ti.xcom_pull(key="video_checksum", dag_id='+DAG_ID+')}}'
                ' --trim_frames {{ti.xcom_pull(key="image_extraction_trim_frames", dag_id='+DAG_ID+')}}'
                ' --frame_width {{ti.xcom_pull(key="image_extraction_frame_width", dag_id='+DAG_ID+')}}'
                ' --file_extension {{ti.xcom_pull(key="extractor_file_extension", dag_id='+DAG_ID+')}}'
                ' --force_run {{ti.xcom_pull(key="image_extraction_force_run", dag_id='+DAG_ID+')}}',
        volumes=['{{ti.xcom_pull(key="volumes_data_path", dag_id='+DAG_ID+')}}'],
        xcom_all=True,
    )

    task_feature_extraction = DockerOperator(
        task_id='feature_extraction',
        image='jacobloe/extract_features:0.7',
        command='/data {{ti.xcom_pull(key="video_checksum", dag_id='+DAG_ID+')}}'
                ' --file_extension {{ti.xcom_pull(key="extractor_file_extension", dag_id='+DAG_ID+')}}'
                ' --force_run {{ti.xcom_pull(key="feature_extraction_force_run", dag_id='+DAG_ID+')}}',
        volumes=['{{ti.xcom_pull(key="volumes_data_path", dag_id='+DAG_ID+')}}',
                 '/home/.keras_ndd/:/root/.keras'],
        xcom_all=True,
    )

    task_update_index = PythonOperator(
        task_id='update_index',
        python_callable=update_index
    )

    task_push_config_to_xcom >> task_get_video >> task_shotdetection >> task_image_extraction >> task_feature_extraction >> task_update_index
