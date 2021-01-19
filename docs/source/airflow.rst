Airflow
=======

Run the image.::

    docker run --rm -it -v airflow_cache:/data -v /var/run/docker.sock:/var/run/docker.sock -p 8080:8080 --network ndd_subnet --name airflow jacobloe/airflow:0.1

If extracted features are to be used for the near duplicate detection "--network ndd_subnet" has to be included.
The networks needs to be the same as the one for the server and client from the near duplicate detection.

In your browser go to `<http://0.0.0.0:8080/>`_ to get access to the airflow webserver.

Start an extractor
^^^^^^^^^^^^^^^^^^

The different extractors are triggered with the airflow_trigger.py. The script needs Python 3 installed. To start the shotdetection use the following command::

    python airflow_trigger.py trigger --dag_id shotdetection --run_id shotdetection_test0

Choose with "--dag_id" which extractor is started. Use "--help" to get a list of the available extractors.
"--run_id" sets a unique id for a extractor which can be used to find it again. If the id was already used, the extractor cannot be started.

Get information about an extractor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The airflow_trigger.py can also be used to get information about any graphs or tasks that are/were runnning.