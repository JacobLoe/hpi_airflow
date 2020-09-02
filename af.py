from datetime import timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.utils.dates import days_ago

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
}

with DAG('hpi', default_args=default_args, schedule_interval=timedelta(minutes=1), catchup=False) as dag:

    task_shot_detection = DockerOperator(
        task_id='shotdetection',
        image='jacobloe/shot_detection:0.1',
        command='/video /data/ /video/file_mappings.tsv',
        volumes=['/home/jacob/Downloads/hpi/videos:/video:ro', '/home/jacob/Downloads/hpi_airflow/static/features_videos:/data'],
    )

    t1 = BashOperator(
        task_id='t1',
        bash_command='echo 1111111111111111111111111111111111111111111111111111111111',
    )

    t2 = BashOperator(
        task_id='t2',
        bash_command='echo 2222222222222222222222222222222222222222222222222222222222',
    )

    task_shot_detection >> t2 >> t1
