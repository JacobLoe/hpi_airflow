from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from docker_operator import DockerOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from rest_requests_tasks import get_videos


DAG_ID = 'feature_extraction'

# default arguments inherited by each task
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'provide_context': True,    # is needed for tasks to communicate via xcom
}


def push_initial_parameters(**context):
    # gets all relevant extractor parameters from the dag configuration and and pushes them to xcom
    # this function should only be called once

    volumes_video_path = context['dag_run'].conf['volumes_video_path']
    volumes_features_path = context['dag_run'].conf['volumes_features_path']
    volumes_file_mappings_path = context['dag_run'].conf['volumes_file_mappings_path']
    extractor_file_extension = context['dag_run'].conf['extractor_file_extension']

    shotdetection_sensitivity = context['dag_run'].conf['shotdetection_sensitivity']
    shotdetection_force_run = context['dag_run'].conf['shotdetection_force_run']

    image_extraction_trim_frames = context['dag_run'].conf['image_extraction_trim_frames']
    image_extraction_frame_width = context['dag_run'].conf['image_extraction_frame_width']
    image_extraction_force_run = context['dag_run'].conf['image_extraction_force_run']

    feature_extraction_force_run = context['dag_run'].conf['feature_extraction_force_run']

    # xcoms are automatically mapped to the task_id and dag_id in which the created to prevent an incorrect pull
    context['ti'].xcom_push(key='volumes_video_path', value=volumes_video_path)
    context['ti'].xcom_push(key='volumes_features_path', value=volumes_features_path)
    context['ti'].xcom_push(key='volumes_file_mappings_path', value=volumes_file_mappings_path)
    context['ti'].xcom_push(key='extractor_file_extension', value=extractor_file_extension)

    context['ti'].xcom_push(key='shotdetection_sensitivity', value=shotdetection_sensitivity)
    context['ti'].xcom_push(key='shotdetection_force_run', value=shotdetection_force_run)

    context['ti'].xcom_push(key='image_extraction_trim_frames', value=image_extraction_trim_frames)
    context['ti'].xcom_push(key='image_extraction_frame_width', value=image_extraction_frame_width)
    context['ti'].xcom_push(key='image_extraction_force_run', value=image_extraction_force_run)

    context['ti'].xcom_push(key='feature_extraction_force_run', value=feature_extraction_force_run)


with DAG(DAG_ID, default_args=default_args,
         schedule_interval=None,
         max_active_runs=1,  # prevents more than one graph from running at a time
         concurrency=1) as dag:

    get_params = PythonOperator(
        task_id='push_params',
        python_callable=push_initial_parameters
    )

    init_video = PythonOperator(
        task_id='get_videos',
        python_callable=get_videos
    )

    shot_detection = (DockerOperator(
        task_id='shotdetection_task',
        image='jacobloe/shot_detection:0.5',
        command='/video /data/ /file_mappings.tsv {{ti.xcom_pull(key="videoid", dag_id='+DAG_ID+')}}'
                ' --sensitivity {{ti.xcom_pull(key="shotdetection_sensitivity", dag_id='+DAG_ID+')}}'
                ' --force_run {{ti.xcom_pull(key="shotdetection_force_run", dag_id='+DAG_ID+')}}',
        volumes=['{{ti.xcom_pull(key="volumes_video_path", dag_id='+DAG_ID+')}}',
                 '{{ti.xcom_pull(key="volumes_features_path", dag_id='+DAG_ID+')}}',
                 '{{ti.xcom_pull(key="volumes_file_mappings_path", dag_id='+DAG_ID+')}}'],
        xcom_all=True,
    ))
    image_extraction = (DockerOperator(
        task_id='image_extraction',
        image='jacobloe/extract_images:0.5',
        command='/video/ /data/ /file_mappings.tsv {{ti.xcom_pull(key="videoid", dag_id='+DAG_ID+')}}'
                ' --trim_frames {{ti.xcom_pull(key="image_extraction_trim_frames", dag_id='+DAG_ID+')}}'
                ' --frame_width {{ti.xcom_pull(key="image_extraction_frame_width", dag_id='+DAG_ID+')}}'
                ' --file_extension {{ti.xcom_pull(key="extractor_file_extension", dag_id='+DAG_ID+')}}'
                ' --force_run {{ti.xcom_pull(key="image_extraction_force_run", dag_id='+DAG_ID+')}}',
        volumes=['{{ti.xcom_pull(key="volumes_video_path", dag_id='+DAG_ID+')}}',
                 '{{ti.xcom_pull(key="volumes_features_path", dag_id='+DAG_ID+')}}',
                 '{{ti.xcom_pull(key="volumes_file_mappings_path", dag_id='+DAG_ID+')}}'],
        xcom_all=True,
    ))
    feature_extraction = (DockerOperator(
        task_id='feature_extraction',
        image='jacobloe/extract_features:0.5',
        command='/data/ /file_mappings.tsv {{ti.xcom_pull(key="videoid", dag_id='+DAG_ID+')}}'
                ' --file_extension {{ti.xcom_pull(key="extractor_file_extension", dag_id='+DAG_ID+')}}'
                ' --force_run {{ti.xcom_pull(key="feature_extraction_force_run", dag_id='+DAG_ID+')}}',
        volumes=['{{ti.xcom_pull(key="volumes_video_path", dag_id='+DAG_ID+')}}',
                 '{{ti.xcom_pull(key="volumes_features_path", dag_id='+DAG_ID+')}}',
                 '{{ti.xcom_pull(key="volumes_file_mappings_path", dag_id='+DAG_ID+')}}',
                 '/home/.keras/:/root/.keras'],
        xcom_all=True,
    ))
    get_params >> init_video >> shot_detection >> image_extraction >> feature_extraction
