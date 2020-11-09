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
    'schedule_interval': None,
    'max_active_runs': 1,   # prevents more than one graph from running at a time
    'concurrency': 1
}


with DAG('optical_flow', default_args=default_args,
         schedule_interval=None,
         max_active_runs=1,  # prevents more than one graph from running at a time
         concurrency=1) as dag:
    task_id = '0'
    vid = '0'

    init = PythonOperator(
        task_id='get_videos',
        python_callable=get_videos
    )
    optical_flow = (DockerOperator(
        task_id='extract_optical_flow_{t}'.format(t=task_id),
        image='jacobloe/optical_flow:0.4',
        command='/video/ /data/ /file_mappings.tsv ' + vid +
                ' --frame_width {{ti.xcom_pull(key="optical_flow_frame_width")}}'
                ' --step_size {{ti.xcom_pull(key="optical_flow_step_size")}}'
                ' --window_size {{ti.xcom_pull(key="optical_flow_window_size")}}'
                ' --top_percentile {{ti.xcom_pull(key="optical_flow_top_percentile")}}'
                ' --force_run {{ti.xcom_pull(key="optical_flow_force_run")}}',
        volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}', '{{ti.xcom_pull(key="volumes_file_mappings_path")}}'],
        xcom_all=True,
    ))

    init >> optical_flow
