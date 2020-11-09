from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from docker_operator import DockerOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from rest_requests import get_videos

# default arguments inherited by each task
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'provide_context': True,    # is needed for tasks to communicate via xcom
}

# FIXME restrict xcoms to the current dag_id

# def push_initial_parameters(**kwargs):
#     # gets all extractor parameters from airflow variables and and pushes them to xcom
#     # this function should only be called once
#
#     volumes_video_path = Variable.get('volumes_video_path')
#     volumes_features_path = Variable.get('volumes_features_path')
#     volumes_file_mappings_path = Variable.get('volumes_file_mappings_path')
#     shotdetection_sensitivity = Variable.get('shotdetection_sensitivity')
#     extractor_file_extension = Variable.get('extractor_file_extension')
#     image_extraction_trim_frames = Variable.get('image_extraction_trim_frames')
#     image_extraction_frame_width = int(Variable.get('image_extraction_frame_width'))
#     optical_flow_frame_width = int(Variable.get('optical_flow_frame_width'))
#     optical_flow_step_size = int(Variable.get('optical_flow_step_size'))
#     optical_flow_window_size = int(Variable.get('optical_flow_window_size'))
#     optical_flow_top_percentile = int(Variable.get('optical_flow_top_percentile'))
#
    # kwargs['ti'].xcom_push(key='volumes_video_path', value=volumes_video_path)
#     kwargs['ti'].xcom_push(key='volumes_features_path', value=volumes_features_path)
#     kwargs['ti'].xcom_push(key='volumes_file_mappings_path', value=volumes_file_mappings_path)
#     kwargs['ti'].xcom_push(key='shotdetection_sensitivity', value=shotdetection_sensitivity)
#     kwargs['ti'].xcom_push(key='shotdetection_force_run', value=)
#     kwargs['ti'].xcom_push(key='extractor_file_extension', value=extractor_file_extension)
#     kwargs['ti'].xcom_push(key='image_extraction_trim_frames', value=image_extraction_trim_frames)
#     kwargs['ti'].xcom_push(key='image_extraction_frame_width', value=image_extraction_frame_width)
#     kwargs['ti'].xcom_push(key='image_extraction_force_run', value=)
#     kwargs['ti'].xcom_push(key='feature_extraction_force_run', value=)
#     kwargs['ti'].xcom_push(key='optical_flow_frame_width', value=optical_flow_frame_width)
#     kwargs['ti'].xcom_push(key='optical_flow_step_size', value=optical_flow_step_size)
#     kwargs['ti'].xcom_push(key='optical_flow_window_size', value=optical_flow_window_size)
#     kwargs['ti'].xcom_push(key='optical_flow_top_percentile', value=optical_flow_top_percentile)
#     kwargs['ti'].xcom_push(key='optical_flow_force_run', value=)


with DAG('shotdetection', default_args=default_args,
         schedule_interval=None,
         max_active_runs=1,  # prevents more than one graph from running at a time
         concurrency=1) as dag:

    videoids = list(Variable.get('videoids').split(' '))  # remove the spaces from the videoid list

    task_id = '0'
    vid = '0'

    init = PythonOperator(
        task_id='get_videos',
        python_callable=get_videos
    )
    # shotdetection = (DockerOperator(
    #     task_id='shotdetection_task_{t}'.format(t=task_id),
    #     image='jacobloe/shot_detection:0.4',
    #     command='/video /data/ /file_mappings.tsv '+vid +
    #             ' --sensitivity {{ti.xcom_pull(key="shotdetection_sensitivity")}}'
    #             ' --force_run {{ti.xcom_pull(key="shotdetection_force_run")}}',
    #     volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}', '{{ti.xcom_pull(key="volumes_file_mappings_path")}}'],
    #     xcom_all=True,
    # ))
    # init >> shotdetection
