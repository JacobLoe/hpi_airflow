from datetime import timedelta
import os
import glob

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
# from airflow.operators.docker_operator import DockerOperator
from docker_operator import DockerOperator
from airflow.utils.dates import days_ago
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.models import Variable

# default arguments inherited by each task
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'provide_context': True,    # is needed for tasks to communicate via xcom
}

with DAG('hpi_extraction', default_args=default_args,
         schedule_interval=None,
         max_active_runs=1,     # prevents more than one graph from running at a time
         concurrency=1
        ) as dag:

    def push_initial_parameters(**kwargs):
        # gets all extractor parameters from airflow variables and and pushes them to xcom
        # this function should only be called once

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


    def check_extractor_progress(**kwargs):
        # checks the feature folders for .done-files of the preceding extractor
        # and returns the ids of the videos that have run successfully

        # check folders for done_files
        volumes_features_path = kwargs['ti'].xcom_pull(key='volumes_features_path')

        # last_extractor should be dynamic instead of hardcoded
        # last_extractor = kwargs['ti'].xcom_pull(key='last_extractor')   # get the name of the last run extractor to search for
        last_extractor = 'shotdetection'

        # search for all the extractor folders in the features path
        features_path = os.path.join(os.path.split(volumes_features_path)[0][:-1], '**', last_extractor)
        all_features = glob.glob(features_path, recursive=True)

        # get the ids of the videos with .done-files
        ids = []
        for f in all_features:
            if os.path.isfile(os.path.join(f, '.done')):
                ids.append(os.path.split(os.path.split(f)[0])[1])
        videoids = ' '.join([i for i in ids])

        # push ids of videos to xcom
        kwargs['ti'].xcom_push(key='videoids', value=videoids)

    get_parameters = PythonOperator(
        task_id='get_parameters',
        python_callable=push_initial_parameters,
    )

    sd = []
    ei = []
    ef = []
    eas = []
    of = []
    videoids = list(Variable.get('videoids').replace(' ', ''))  # remove the spaces from the videoid list
    for i, vid in enumerate(videoids):
        # create a chain of extractor task for each videoid idividually
        sd.append(DockerOperator(
            task_id='shotdetection_task_{t}'.format(t=str(i)),
            image='jacobloe/shot_detection:0.2',
            command='/video /data/ /file_mappings.tsv {id} --sensitivity {{ti.xcom_pull(key="shotdetection_sensitivity")}}'.format(id=vid),
            volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}', '{{ti.xcom_pull(key="volumes_file_mappings_path")}}'],
            xcom_all=True,
        ))
        ei.append(BashOperator(
            task_id='ei{}'.format(i),
            bash_command='echo {}'.format(vid),
        ))
        ef.append(BashOperator(
            task_id='ef{}'.format(i),
            bash_command='echo {}'.format(vid),
        ))
        eas.append(BashOperator(
            task_id='eas{}'.format(i),
            bash_command='echo {}'.format(vid),
        ))
        of.append(BashOperator(
            task_id='of{}'.format(i),
            bash_command='echo {}'.format(vid),
        ))

        # tasks for each id are chained together sequentially
        sd[i] >> ei[i] >> ef[i] >> eas[i] >> of[i]

    # all task chains are dependent on a initial task
    get_parameters >> sd
