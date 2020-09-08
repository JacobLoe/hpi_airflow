# airflow webserver -p 8080
# airflow scheduler

from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.utils.dates import days_ago
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.models import Variable

# default arguments inherited by each task
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'retries': 3,
    'retry_delay': timedelta(hours=1),
}


with DAG('hpi_extraction', default_args=default_args, schedule_interval=timedelta(seconds=5),) as dag:

    # the volumes mounted to the image need to be given as absolute paths
    volumes_video_path = Variable.get('volumes_video_path')     # '/home/jacob/Downloads/hpi/videos:/video:ro'
    volumes_features_path = Variable.get('volumes_features_path')       # '/home/jacob/Downloads/hpi_airflow/static/features_videos:/data'
    volumes_file_mappings_path = Variable.get('volumes_file_mappings_path')     # '/home/jacob/Downloads/hpi/videos/file_mappings.tsv:/file_mappings.tsv:ro'

    video_ids = '0 1 2'

    t1 = BashOperator(
        task_id='t1',
        bash_command='echo {{var.value.volumes_video_path}}',
    )

    task_shot_detection = DockerOperator(
        task_id='shotdetection',
        image='jacobloe/shot_detection:0.1',
        command='/video /data/ /file_mappings.tsv {videoids}'.format(videoids=video_ids),
        volumes=[volumes_video_path, volumes_features_path, volumes_file_mappings_path],
    )
    #
    # trim_frames = '--trim_frames yes'
    # frame_width = '--frame_width 400'
    #
    # task_extract_images = DockerOperator(
    #     task_id='image_extraction',
    #     image='jacobloe/extract_images:0.1',
    #     command='/video/ /data/ /file_mappings.tsv {a} {b}'.format(a=trim_frames, b=frame_width),
    #     volumes=[volumes_video_path, volumes_features_path, volumes_file_mappings_path],
    # )
    #
    # task_extract_features = DockerOperator(
    #     task_id='feature_extraction',
    #     image='jacobloe/extract_features:0.1',
    #     command='/data/ /file_mappings.tsv',
    #     volumes=[volumes_video_path, volumes_features_path, volumes_file_mappings_path, '/home/.keras/:/root/.keras'],
    # )
    #
    # task_extract_aspect_ratio = DockerOperator(
    #     task_id='aspect_ratio_extraction',
    #     image='jacobloe/extract_aspect_ratio:0.1',
    #     command='/data/ /file_mappings.tsv',
    #     volumes=[volumes_video_path, volumes_features_path, volumes_file_mappings_path],
    # )
    #
    # task_extract_optical_flow = DockerOperator(
    #     task_id='extract_optical_flow',
    #     image='jacobloe/optical_flow:0.1',
    #     command='/video/ /data /file_mappings.tsv',
    #     volumes=[volumes_video_path, volumes_features_path, volumes_file_mappings_path],
    # )
    #

    # templated_command = """
    # {% for i in range(5) %}
    #     echo "{{ ds }}"
    #     echo "{{ macros.ds_add(ds, 7)}}"
    #     echo "{{ params.my_param }}"
    # {% endfor %}
    # """
    #
    # t3 = BashOperator(
    #     task_id='t3',
    #     depends_on_past=False,
    #     bash_command=templated_command,
    #     params={'my_param': 'Parameter I passed in'},
    #     xcom_push=True
    # )
    # # tasks will be executed from left to right, tasks will only run if the preceding task was executed successfully
    # # tasks no explicitly mentioned are executed independently of other task and run in order of their appearance in the code
    # task_shot_detection >> task_extract_images
    # task_extract_images >> [task_extract_features, task_extract_aspect_ratio]
