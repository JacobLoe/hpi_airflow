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
    'start_date': days_ago(1),
    'retries': 3,
    'retry_delay': timedelta(hours=1),
    'provide_context': True,    # is needed for tasks to communicate via xcom
}

with DAG('hpi_extraction', default_args=default_args,
         schedule_interval=timedelta(seconds=10),
         max_active_runs=1,
         concurrency=1,) as dag:

    videoids = Variable.get('videoids')

    def push_initial_videoids(**kwargs):
        # gets ids from airflow variable and and push them to xcom
        # this function is only called once
        kwargs['ti'].xcom_push(key='videoids', value=videoids)

    def process_videoids(**kwargs):
        # gets ids from another task
        ti = kwargs['ti']
        ids = ti.xcom_pull(key='videoids')
        print('ids: ', ids)
        # run docker images with pulled ids
        # instead for testing assume one video was not processed correctly and push the other ids
        new_ids = ids[:-2]
        print('new_ids: ', new_ids)
        kwargs['ti'].xcom_push(key='videoids', value=new_ids)


    def check_extractor_progress(**kwargs):
        # check folders for done_files
        # for testing pull ids from xcom and push them unchanged
        ti = kwargs['ti']
        ids = ti.xcom_pull(key='videoids')
        print('ids: ', ids)
        # push ids of movies with the files
        kwargs['ti'].xcom_push(key='videoids', value=ids)

    t1 = PythonOperator(
        task_id='push_initial_video_ids',
        python_callable=push_initial_videoids,
    )

    t2 = PythonOperator(
        task_id='process_videoids',
        python_callable=process_videoids,
    )

    t3 = PythonOperator(
        task_id='check_extractor_progress',
        python_callable=check_extractor_progress,
    )

    t4 = PythonOperator(
        task_id='t4',
        python_callable=process_videoids,
    )

    t5 = PythonOperator(
        task_id='t5',
        python_callable=check_extractor_progress,
    )

    t1 >> t2 >> t3 >> t4 >> t5
    # # the volumes mounted to the image need to be given as absolute paths
    # volumes_video_path = Variable.get('volumes_video_path')
    # # volumes_features_path = Variable.get('volumes_features_path')
    # # volumes_file_mappings_path = Variable.get('volumes_file_mappings_path')
    # #
    # # # docker parameters
    # # shotdetection_sensitivity = Variable.get('shotdetection_sensitivity')
    # #
    # # image_extraction_trim_frames = Variable.get('image_extraction_trim_frames')
    # # image_extraction_frame_width = Variable.get('image_extraction_frame_width')
    # # # FIXME maybe use the same file_extension variable for all extractors to prevent errors
    # # image_extraction_file_extension = Variable.get('image_extraction_file_extension')
    # #
    # # feature_extraction_file_extension = Variable.get('feature_extraction_file_extension')
    # #
    # # aspect_ratio_extraction_file_extension = Variable.get('aspect_ratio_extraction_file_extension')
    # #
    # # optical_flow_frame_width = Variable.get('optical_flow_frame_width')
    # # optical_flow_step_size = Variable.get('optical_flow_step_size')
    # # optical_flow_window_size = Variable.get('optical_flow_window_size')
    # # optical_flow_top_percentile = Variable.get('optical_flow_top_percentile')
    #

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
