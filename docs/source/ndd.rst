.. _ndd:

Near duplicate detection
========================

If you want to run any independently of airflow use the commands in :ref:`extractors`.

server
^^^^^^

The server has to be started for the feature extraction in airflow to run successful. First make sure the *airflow_cache* docker volume and the docker network *ndd_subnet* exist::

    $ docker volume create --driver local --opt type=none --opt device=/home/jacob/Downloads/hpi/data --opt o=bind airflow_cache
    $ docker network create --driver bridge ndd_subnet

Start the server with the following command::

    $ docker run --rm -it -v airflow_cache:/data -p 9000:9000 --network ada_subnet -v /home/.keras_ndd/:/root/.keras --name server_ndd jacobloe/server_ndd:1.0

On startup this creates a folder *.keras_ndd* in */home* and maps it to */root/.keras* in the docker container.
This is done to save the model that is downloaded by the server and the feature extraction, in a way that doesn't interfere with other models downloaded into *home/.keras*.

The server will first create an index from all features in the *airflow_cache* that were extracted correctly. The progress can be seen in the command line.
After the index was created the server is ready to serve requests.

client
^^^^^^

The client uses the same network as the server::

    $ docker network create --driver bridge ndd_subnet

To start the client use::

    $ docker run --rm -it -p 8000:80 --network ada_subnet --name client_flask jacobloe/client_flask:1.0

The client can be accessed through a browser on `<http://0.0.0.0:8000/imagesearch/>`_.
By clicking on the button *Choose File*, one can upload an image from the pc. Clicking on *Upload* will then send the image to the server and then return the results.
Depending on the size of the index the process may take a minute.

The number of results displayed can be adjusted by entering a positive integer in the box to the left of the *Upload*-Button, before submitting an image.

By checking the checkbox *remove letterbox* any letterbox around the uploaded image will be removed before searching for duplicate images.

folder structure
^^^^^^^^^^^^^^^^

The extractors will create the following folder structure (and assume that results are stored this way). The name of folder *data* doesn't matter
The folder also contains the logs for airflow.

.. code-block:: bash

    data
    ├── VIDEOID0
    │   ├── shotdetect
    │       ├── result.csv
    │       └── .done
    │   ├── frames
    │       ├── TIMESTAMP.jpeg
    │       ├── TIMESTAMP.jpeg
    │       └── .done
    │   ├── features
    │       ├── TIMESTAMP.npy
    │       ├── TIMESTAMP.npy
    │       └── .done
    │   ├── aspectratio
    │       ├── VIDEOID0.csv
    │       └── .done
    │   ├── opticalflow
    │       ├── VIDEOID0.csv
    │       └── .done
    │   └── media
    │       ├── VIDEOID0.mp4
    │       └── .done
    ├── VIDEOID1
    │   ├── shotdetect
    │   ├── frames
    │   ├── features
    │   ├── aspectratio
    │   ├── opticalflow
    │   └── media
    ├── airflow
    │   └── logs
    │       ├── aspect_ratio_extraction
    │           ├── aspect_ratio_extraction
    │               ├── DAG0_EXECUTION_DATE
    │                   └── 1.log
    │               └── DAG1_EXECUTION_DATE
    │           ├── get_video
    │           ├── image_extraction
    │           ├── push_config_to_xcom
    │           └── shotdetection
    │       ├── feature_extraction
    │       ├── optical_flow
    │       └── shotdetection
