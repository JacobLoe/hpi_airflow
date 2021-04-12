.. _installation:

installation
============

Clone the repository from `<https://github.com/ProjectAdA/ada-va>`_

Move into the folder *ada-va* of the repository::

    cd ada-va/ada-va


extractors
----------

Build the Dockerfiles for the extractors::

    docker-compose -f docker-compose.extractors.yml build

The imagesearch client is built with ::

    docker build -f docker/Dockerfile_client_flask -t ada-va/client_flask:1.0 .

airflow
-------

First create volumes for the cache and logs fro airflow::

    mkdir -p ./volumes/ada-va-cache && mkdir -p ./volumes/airflow-logs

Refer to :ref:`folder_structure` to see how the volume is structured.
Initialize the database::

    docker network create ada-rproxy
    docker-compose -f docker-compose.yml up init

Start the airflow stack::

    docker-compose -f docker-compose.yml up

Configuration
-------------

The docker-compose files is configured with three files.

* .env
* secrets.env
* ada-va.cfg
* airflow.env

*.env* sets the versions of python, the postgres database and airflow. The names of the extractor docker images are also set here.

*secrets.env* contains the credentials that docker-compose uses to set the users for the services used by ada-va (database, airflow ..).
The values have to be filled out by hand and not be pushed onto the repository.

*ada-va.cfg* contains the default parameters for the extractors as well parameters shared by all extractors.

* adava_cache_dir
* docker_url
* shotdetection sensitivity
* deepfeatures frame_width