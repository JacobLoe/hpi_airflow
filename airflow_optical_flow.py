from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from docker_operator import DockerOperator
from airflow.utils.dates import days_ago
from get_video import get_video

DAG_ID = 'optical_flow'

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
    get_video_force_run = context['dag_run'].conf['get_video_force_run']

    optical_flow_frame_width = context['dag_run'].conf['optical_flow_frame_width']
    optical_flow_step_size = context['dag_run'].conf['optical_flow_step_size']
    optical_flow_window_size = context['dag_run'].conf['optical_flow_window_size']
    optical_flow_top_percentile = context['dag_run'].conf['optical_flow_top_percentile']
    optical_flow_force_run = context['dag_run'].conf['optical_flow_force_run']

    # xcoms are automatically mapped to the task_id and dag_id in which the created to prevent an incorrect pull
    context['ti'].xcom_push(key='videoid', value=videoid)

    context['ti'].xcom_push(key='volumes_data_path', value=volumes_data_path)
    context['ti'].xcom_push(key='get_video_force_run', value=get_video_force_run)

    context['ti'].xcom_push(key='optical_flow_frame_width', value=optical_flow_frame_width)
    context['ti'].xcom_push(key='optical_flow_step_size', value=optical_flow_step_size)
    context['ti'].xcom_push(key='optical_flow_window_size', value=optical_flow_window_size)
    context['ti'].xcom_push(key='optical_flow_top_percentile', value=optical_flow_top_percentile)
    context['ti'].xcom_push(key='optical_flow_force_run', value=optical_flow_force_run)


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

    task_optical_flow = (DockerOperator(
        task_id='extract_optical_flow',
        image='jacobloe/optical_flow:1.0',
        command='/data/ {{ti.xcom_pull(key="video_checksum", dag_id='+DAG_ID+')}}'
                ' --frame_width {{ti.xcom_pull(key="optical_flow_frame_width", dag_id='+DAG_ID+')}}'
                ' --step_size {{ti.xcom_pull(key="optical_flow_step_size", dag_id='+DAG_ID+')}}'
                ' --window_size {{ti.xcom_pull(key="optical_flow_window_size", dag_id='+DAG_ID+')}}'
                ' --top_percentile {{ti.xcom_pull(key="optical_flow_top_percentile", dag_id='+DAG_ID+')}}'
                ' --force_run {{ti.xcom_pull(key="optical_flow_force_run", dag_id='+DAG_ID+')}}',
        volumes=['{{ti.xcom_pull(key="volumes_data_path", dag_id='+DAG_ID+')}}'],
        xcom_all=True,
    ))

    task_push_config_to_xcom >> task_get_video >> task_optical_flow
