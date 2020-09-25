from datetime import timedelta
import os
import glob

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
    'start_date': days_ago(1),
    'retries': 3,
    'retry_delay': timedelta(hours=1),
    'provide_context': True,    # is needed for tasks to communicate via xcom
}

with DAG('hpi_extraction', default_args=default_args,
         schedule_interval=timedelta(seconds=10),
         max_active_runs=1,     # prevents more than one graph from running at a time
        ) as dag:

    def push_initial_parameters(**kwargs):
        # gets all extractor parameters from airflow variables and and push them to xcom
        # this function should only be called once

        videoids = Variable.get('videoids')
        volumes_video_path = Variable.get('volumes_video_path')
        volumes_features_path = Variable.get('volumes_features_path')
        volumes_file_mappings_path = Variable.get('volumes_file_mappings_path')
        shotdetection_sensitivity = Variable.get('shotdetection_sensitivity')
        extractor_file_extension = Variable.get('extractor_file_extension')
        image_extraction_trim_frames = Variable.get('image_extraction_trim_frames')
        image_extraction_frame_width = Variable.get('image_extraction_frame_width')
        optical_flow_frame_width = Variable.get('optical_flow_frame_width')
        optical_flow_step_size = Variable.get('optical_flow_step_size')
        optical_flow_window_size = Variable.get('optical_flow_window_size')
        optical_flow_top_percentile = Variable.get('optical_flow_top_percentile')

        kwargs['ti'].xcom_push(key='videoids', value=videoids)
        kwargs['ti'].xcom_push(key='volumes_video_path', value=volumes_video_path)
        kwargs['ti'].xcom_push(key='volumes_features_path', value=volumes_features_path)
        kwargs['ti'].xcom_push(key='volumes_file_mappings_path', value=volumes_file_mappings_path)
        kwargs['ti'].xcom_push(key='shotdetection_sensitivity', value=shotdetection_sensitivity)
        kwargs['ti'].xcom_push(key='extractor_file_extension', value=extractor_file_extension)
        kwargs['ti'].xcom_push(key='image_extraction_trim_frames', value=image_extraction_trim_frames)
        kwargs['ti'].xcom_push(key='image_extraction_frame_width', value=image_extraction_frame_width)
        kwargs['ti'].xcom_push(key='optical_flow_frame_width', value=optical_flow_frame_width)
        kwargs['ti'].xcom_push(key='optical_flow_step_size', value=optical_flow_step_size)
        kwargs['ti'].xcom_push(key='optical_flow_window_size', value=optical_flow_window_size)
        kwargs['ti'].xcom_push(key='optical_flow_top_percentile', value=optical_flow_top_percentile)

    def process_videoids(**kwargs):
        # gets ids from another task
        ti = kwargs['ti']
        ids = ti.xcom_pull(key='videoids')
        print('ids: ', ids)
        # run docker images with pulled ids
        #
        # instead for testing assume one video was not processed correctly and push the other ids
        new_ids = ids[:-2]
        print('new_ids: ', new_ids)
        kwargs['ti'].xcom_push(key='videoids', value=new_ids)


    def check_extractor_progress(**kwargs):
        # check folders for done_files
        # volumes_features_path = kwargs['ti'].xcom_pull(key='volumes_features_path')
        # last_extractor = kwargs['ti'].xcom_pull(key='last_extractor')   # get the name of the last run extractor to search for
        # features_path = os.path.join(os.path.split(volumes_features_path),**,last_extractor)
        # pp = glob.glob(features_path)
        # ids = ' '
        # for p in pp:
        #     if os.isfile(os.path.join(p, ./done)):
        #          id = os.path.split(os.path.split(p)[0])[1]
        #           ids.join(id)
        # for testing pull ids from xcom and push them unchanged
        ti = kwargs['ti']
        ids = ti.xcom_pull(key='videoids')
        print('ids: ', ids)
        # push ids of movies with the files
        kwargs['ti'].xcom_push(key='videoids', value=ids)

    t1 = BashOperator(
        task_id='t1',
        bash_command='sleep 30'
    )

    t2 = BashOperator(
        task_id='t2',
        bash_command='sleep 30'
    )
    t1 >> t2

    # task_shotdetection = DockerOperator(
    #     task_id='shotdetection',
    #     image='jacobloe/shot_detection:0.1',
    #     command='/video /data/ /file_mappings.tsv {videoids} --sensitivity {sensitivity}'.format(
    #         videoids=videoids, sensitivity=shotdetection_sensitivity),
    #     volumes=[volumes_video_path, volumes_features_path, volumes_file_mappings_path],
    # )

    # task_extract_images = DockerOperator(
    #     task_id='image_extraction',
    #     image='jacobloe/extract_images:0.1',
    #     command='/video/ /data/ /file_mappings.tsv {videoids} --trim_frames {trim_frames} --frame_width {frame_width} --file_extension {file_extension}'.format(
    #         videoids=videoids, trim_frames=image_extraction_trim_frames, frame_width=image_extraction_frame_width, file_extension=image_extraction_file_extension),
    #     volumes=[volumes_video_path, volumes_features_path, volumes_file_mappings_path],
    # )
    #
    # task_extract_features = DockerOperator(
    #     task_id='feature_extraction',
    #     image='jacobloe/extract_features:0.1',
    #     command='/data/ /file_mappings.tsv {videoids} --file_extension {file_extension}'.format(
    #         videoids=videoids, file_extension=feature_extraction_file_extension),
    #     volumes=[volumes_video_path, volumes_features_path, volumes_file_mappings_path, '/home/.keras/:/root/.keras'],
    # )
    #
    # task_extract_aspect_ratio = DockerOperator(
    #     task_id='aspect_ratio_extraction',
    #     image='jacobloe/extract_aspect_ratio:0.1',
    #     command='/data/ /file_mappings.tsv {videoids} --file_extension {file_extension}'.format(
    #         videoids=videoids, file_extension=aspect_ratio_extraction_file_extension),
    #     volumes=[volumes_video_path, volumes_features_path, volumes_file_mappings_path],
    # )
    #
    # task_extract_optical_flow = DockerOperator(
    #     task_id='extract_optical_flow',
    #     image='jacobloe/optical_flow:0.1',
    #     command='/video/ /data /file_mappings.tsv {videoids} --frame_width {frame_width} --step_size {step_size} --window_size {window_size} --top_percentile {top_percentile}'.format(
    #         videoids=videoids, step_size=optical_flow_step_size, window_size=optical_flow_window_size, frame_width=optical_flow_frame_width, top_percentile=optical_flow_top_percentile),
    #     volumes=[volumes_video_path, volumes_features_path, volumes_file_mappings_path],
    # )
    #
    # # # tasks will be executed from left to right, tasks will only run if the preceding task was executed successfully
    # # # tasks no explicitly mentioned are executed independently of other task and run in order of their appearance in the code
    # task_shotdetection >> task_extract_images
    # task_extract_images >> [task_extract_features, task_extract_aspect_ratio]
