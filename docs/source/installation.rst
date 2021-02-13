installation
============

Clone the repository from `<https://github.com/JacobLoe/hpi_airflow>`_

Move into the repo::

    $ cd hpi_airflow

Build the Dockerfile::

    $ docker build -f Dockerfile_airflow -t jacobloe/airflow:1.0 .

Create a volume for the video data::

    $ docker volume create --driver local --opt type=none --opt device=ABSOLUTE_PATH_TO_DATA --opt o=bind airflow_cache

Create the docker subnet for the communication between airflow and the ndd server::

    $ docker network create --driver bridge ndd_subnet

