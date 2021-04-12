.. _folder_structure:

folder structure
================

The extractors will create the following folder structure (and assume that results are stored this way).
The folder also contains the logs for airflow.

.. code-block:: bash

    volumes
    ├── adava-cache
    │   ├── VIDEOID0
    │       ├── shotdetect
    │              ├── result.csv
    │           └── .done
    │       ├── frames
    │           ├── TIMESTAMP.jpeg
    │           ├── TIMESTAMP.jpeg
    │           └── .done
    │       ├── features
    │           ├── TIMESTAMP.npy
    │           ├── TIMESTAMP.npy
    │           └── .done
    │       ├── aspectratio
    │           ├── VIDEOID0.csv
    │           └── .done
    │       ├── opticalflow
    │           ├── VIDEOID0.csv
    │           └── .done
    │       └── media
    │           ├── VIDEOID0.mp4
    │           └── .done
    │   ├── VIDEOID1
    │       ├── shotdetect
    │       ├── frames
    │       ├── features
    │       ├── aspectratio
    │       ├── opticalflow
    │       └── media
    │   └── .keras
    │       └── models
    │           └── inception_resnet_v2_weights_tf_dim_ordering_tf_kernels.h5
    ├── airflow-logs
    │   ├── shotdetection
    │       ├── shotdetection.extract_shots
    │           ├── DAG0_EXECUTION_DATE
    │               └── 1.log
    │           └── DAG1_EXECUTION_DATE
    │       ├── shotdetection.videodata.get_video_metadata
    │       └── shotdetection.videodata.get_video_file
    │   ├── deepfeatures
    │   ├── scheduler
    │       ├── DATE0
    │           └── utils
    │               ├── configuration.py.log
    │               └── setup.py.log
    │           ├── airflow_advene_sound.py.log
    │           ├── airflow_aspect_ratio_extraction.py.log
    │           ├── ......
    │       └── DATE1
    │   └── dag_process_manager
    │       └── dag_process_manager.log
