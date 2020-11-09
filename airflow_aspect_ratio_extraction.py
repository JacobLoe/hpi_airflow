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


with DAG('aspect_ratio_extraction', default_args=default_args,
         schedule_interval=None,
         max_active_runs=1,     # prevents more than one graph from running at a time
         concurrency=1) as dag:

    task_id = '0'
    vid = '0'

    init = PythonOperator(
        task_id='get_videos',
        python_callable=get_videos
    )
    shot_detection = (DockerOperator(
        task_id='shotdetection_task_{t}'.format(t=task_id),
        image='jacobloe/shot_detection:0.4',
        command='/video /data/ /file_mappings.tsv '+vid +
                ' --sensitivity {{ti.xcom_pull(key="shotdetection_sensitivity")}}'
                ' --force_run {{ti.xcom_pull(key="shotdetection_force_run")}}',
        volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}', '{{ti.xcom_pull(key="volumes_file_mappings_path")}}'],
        xcom_all=True,
    ))
    image_extraction = (DockerOperator(
        task_id='image_extraction_{t}'.format(t=task_id),
        image='jacobloe/extract_images:0.4',
        command='/video/ /data/ /file_mappings.tsv '+vid +
                ' --trim_frames {{ti.xcom_pull(key="image_extraction_trim_frames")}}'
                ' --frame_width {{ti.xcom_pull(key="image_extraction_frame_width")}}'
                ' --file_extension {{ti.xcom_pull(key="extractor_file_extension")}}'
                ' --force_run {{ti.xcom_pull(key="image_extraction_force_run")}}',
        volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}', '{{ti.xcom_pull(key="volumes_file_mappings_path")}}'],
        xcom_all=True,
    ))
    aspect_ratio_extraction = (DockerOperator(
        task_id='aspect_ratio_extraction_{t}'.format(t=task_id),
        image='jacobloe/extract_aspect_ratio:0.4',
        command='/video /data/ /file_mappings.tsv '+vid +
                ' --file_extension {{ti.xcom_pull(key="extractor_file_extension")}}'
                ' --force_run {{ti.xcom_pull(key="aspect_ratio_extraction_force_run")}}',
        volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}', '{{ti.xcom_pull(key="volumes_file_mappings_path")}}'],
        xcom_all=True,
    ))
    init >> shot_detection >> image_extraction >> aspect_ratio_extraction
