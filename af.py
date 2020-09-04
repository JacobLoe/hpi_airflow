# airflow webserver -p 8080
# airflow scheduler

from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.utils.dates import days_ago

# default arguments inherited by each task
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'retries': 3,
    'retry_delay': timedelta(hours=1),
}

with DAG('hpi_extraction', default_args=default_args, schedule_interval=timedelta(hours=2),) as dag:


    # task_detect_new_movie =

    task_shot_detection = DockerOperator(
        task_id='shotdetection',
        image='jacobloe/shot_detection:0.1',
        command='/video /data/ /video/file_mappings.tsv',
        # the volumes mounted to the image need to be given as absolute paths
        volumes=['/home/jacob/Downloads/hpi/videos:/video:ro', '/home/jacob/Downloads/hpi_airflow/static/features_videos:/data'],
    )

    task_extract_images = DockerOperator(
        task_id='image_extraction',
        image='jacobloe/extract_images:0.1',
        command='/video /data/ /video/file_mappings.tsv',
        volumes=['/home/jacob/Downloads/hpi/videos:/video:ro', '/home/jacob/Downloads/hpi_airflow/static/features_videos:/data'],
    )

    task_extract_features = DockerOperator(
        task_id='feature_extraction',
        image='jacobloe/extract_features:0.1',
        command='/data/ /video/file_mappings.tsv',
        volumes=['/home/jacob/Downloads/hpi/videos:/video:ro', '/home/jacob/Downloads/hpi_airflow/static/features_videos:/data', '/home/.keras/:/root/.keras'],
    )

    task_extract_aspect_ratio = DockerOperator(
        task_id='aspect_ratio_extraction',
        image='jacobloe/extract_aspect_ratio:0.1',
        command='/data/ /video/file_mappings.tsv',
        volumes=['/home/jacob/Downloads/hpi/videos:/video:ro', '/home/jacob/Downloads/hpi_airflow/static/features_videos:/data'],
    )

    task_extract_optical_flow = DockerOperator(
        task_id='extract_optical_flow',
        image='jacobloe/optical_flow:0.1',
        command='/video /data /video/file_mappings.tsv',
        volumes=['/home/jacob/Downloads/hpi/videos:/video:ro', '/home/jacob/Downloads/hpi_airflow/static/features_videos:/data'],
    )

    # tasks will be executed from left to right, tasks will only run if the preceding task was executed succesfully
    #
    task_shot_detection >> task_extract_images
    task_extract_images >> [task_extract_features, task_extract_aspect_ratio]
