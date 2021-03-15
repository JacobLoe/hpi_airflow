.. _installation:

installation
============

Clone the repository from `<https://github.com/ProjectAdA/ada-va>`_

Move into the repo::

    cd ada-va

airflow
-------

Build the Dockerfile::

    docker build -f ada-va/docker/Dockerfile_airflow -t jacobloe/airflow:1.0 ada-va

extractors
----------

Build the Dockerfiles::

    docker build -f ada-va/docker/Dockerfile_shot_detection -t jacobloe/shotdetect:1.0 ada-va
    docker build -f ada-va/docker/Dockerfile_extract_images -t jacobloe/extract_images:1.0 ada-va
    docker build -f ada-va/docker/Dockerfile_extract_aspect_ratio -t jacobloe/extract_aspect_ratio:1.0 ada-va
    docker build -f ada-va/docker/Dockerfile_extract_features -t jacobloe/extract_features:1.0 ada-va

    docker build -f ada-va/docker/Dockerfile_optical_flow -t jacobloe/optical_flow:1.0 ada-va

    docker build -f ada-va/docker/Dockerfile_transcribe_audio -t jacobloe/transcribe_audio:1.0 ada-va

Airflow assumes the images exist with the names in the format *jacobLoe/<extractor_name>:1.0*. If other names are wanted the in the relevant airflow-files has to changed.

The server and client are built::

    docker build -f ada-va/docker/Dockerfile_server_ndd -t jacobloe/server_ndd:1.0 ada-va
    docker build -f ada-va/docker/Dockerfile_client_flask -t jacobloe/client_flask:1.0 ada-va

additional requirements
-----------------------

All docker images share a volume to write/read the video data and logs. The path defined with *devide=* has to be an absolute path::

    docker volume create --driver local --opt type=none --opt device=ABSOLUTE_PATH_TO_DATA --opt o=bind airflow_cache

The docker images also need a docker subnet to communicate between each other::

    docker network create --driver bridge ada_subnet

