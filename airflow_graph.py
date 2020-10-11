from datetime import timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from docker_operator import DockerOperator
from airflow.utils.dates import days_ago
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
        image_extraction_frame_width = int(Variable.get('image_extraction_frame_width'))
        optical_flow_frame_width = int(Variable.get('optical_flow_frame_width'))
        optical_flow_step_size = int(Variable.get('optical_flow_step_size'))
        optical_flow_window_size = int(Variable.get('optical_flow_window_size'))
        optical_flow_top_percentile = int(Variable.get('optical_flow_top_percentile'))

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
        # create a chain of extractor task for each videoid individually
        # docker commands have to be formatted without '.format()' as it clashes with the jinja templates for xcom
        sd.append(DockerOperator(
            task_id='shotdetection_task_{t}'.format(t=str(i)),
            image='jacobloe/shot_detection:0.2',
            command='/video /data/ /file_mappings.tsv '+vid +
                    ' --sensitivity {{ti.xcom_pull(key="shotdetection_sensitivity")}}',
            volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}', '{{ti.xcom_pull(key="volumes_file_mappings_path")}}'],
            xcom_all=True,
        ))
        ei.append(DockerOperator(
            task_id='image_extraction_{t}'.format(t=str(i)),
            image='jacobloe/extract_images:0.2',
            command='/video/ /data/ /file_mappings.tsv '+vid +
                    ' --trim_frames {{ti.xcom_pull(key="image_extraction_trim_frames")}} '
                    '--frame_width {{ti.xcom_pull(key="image_extraction_frame_width")}} '
                    '--file_extension {{ti.xcom_pull(key="extractor_file_extension")}}',
            volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}', '{{ti.xcom_pull(key="volumes_file_mappings_path")}}'],
            xcom_all=True,
        ))
        ef.append(DockerOperator(
            task_id='feature_extraction_{t}'.format(t=str(i)),
            image='jacobloe/extract_features:0.2',
            command='/video/ /data/ /file_mappings.tsv '+vid +
                    ' --file_extension {{ti.xcom_pull(key="extractor_file_extension")}}',
            volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}',
                     '{{ti.xcom_pull(key="volumes_file_mappings_path")}}', '/home/.keras/:/root/.keras'],
            xcom_all=True,
        ))
        eas.append(DockerOperator(
            task_id='aspect_ratio_extraction_{t}'.format(t=str(i)),
            image='jacobloe/extract_aspect_ratio:0.2',
            command='/video/ /data/ /file_mappings.tsv '+vid +
                    ' --file_extension {{ti.xcom_pull(key="extractor_file_extension")}}',
            volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}', '{{ti.xcom_pull(key="volumes_file_mappings_path")}}'],
            xcom_all=True,
        ))
        of.append(DockerOperator(
            task_id='extract_optical_flow_{t}'.format(t=str(i)),
            image='jacobloe/optical_flow:0.2',
            command='/video/ /data/ /file_mappings.tsv '+vid +
                    '--frame_width {{ti.xcom_pull(key="optical_flow_frame_width")}} '
                    '--step_size {{ti.xcom_pull(key="optical_flow_step_size")}} '
                    '--window_size {{ti.xcom_pull(key="optical_flow_window_size")}} '
                    '--top_percentile {{ti.xcom_pull(key="optical_flow_top_percentile")}}',
            volumes=['{{ti.xcom_pull(key="volumes_video_path")}}', '{{ti.xcom_pull(key="volumes_features_path")}}', '{{ti.xcom_pull(key="volumes_file_mappings_path")}}'],
            xcom_all=True,
        ))

        # tasks for each id are chained together sequentially, image extraction is dependent ond shotdetection, feature extraction on imageextraction ...
        sd[i] >> ei[i] >> ef[i] >> eas[i] >> of[i]

    # all task chains are dependent on a initial task
    get_parameters >> sd
