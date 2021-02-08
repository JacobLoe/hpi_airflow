Airflow
=======

Run the image.::

    $ docker run --rm -it -v airflow_cache:/data -v /var/run/docker.sock:/var/run/docker.sock -p 8080:8080 --network ndd_subnet --name airflow jacobloe/airflow:1.0

If extracted features are to be used for the near duplicate detection "--network ndd_subnet" has to be included.
The networks needs to be the same as the one for the server and client from the near duplicate detection.

In your browser go to `<http://0.0.0.0:8080/>`_ to get access to the airflow webserver.

Start an extractor
------------------

The different extractors are triggered with the airflow_trigger.py. The script needs Python 3 installed. To start the shotdetection use the following command::

    $ python airflow_trigger.py trigger --dag_id shotdetection --run_id shotdetection_test0

Choose with "--dag_id" which extractor is started. Use "--help" to get a list of the available extractors.
"--run_id" sets a unique id for a extractor which can be used to find it again. If the id was already used, the extractor cannot be started.

Whenever a extractor has run successfully a *.done-file* will be written which includes the date the extractor was last changed and the parameters that were used to run it.
If the same extractor is run again, the extraction for any results for which the content of the *.done-file* matches the parameters of the current extractor will be skipped.
Optionally each extractor (including the tasks *update_index* and *get_video*) has a parameter *force_run* which if set to *True* forces the extractor to run again regardless
of the *.done-file*.

Extractor configuration
^^^^^^^^^^^^^^^^^^^^^^^

The parameters of the extractors are defined in the file *config.json* and can be easily changed there. Information on the effect of each parameter can be found in the extractor scripts themselves.

Each time an extractor is triggered with the script, its send the parameters to the airflow server and where they will first be copied to airflow variables called *xcom*.
*Xcoms* are unique for each graph in airflow so this its made sure that changing starting a new extractor with different parameters interfere with other parameters.

An explanation of all the parameters can be found here: :ref:`extractor_configuration`.

Get information about an extractor
----------------------------------

The airflow_trigger.py can also be used to get information about any graphs or tasks that are/were runnning. The commands only work if the airflow webserver is running.
With "--help" you get list of the possible positional arguments "trigger, get_dag_info, ...".
For each of options the optional arguments can be combined freely to get a range of different information back.

DAGs
^^^^

Use the following command to get a list of all dags that have run::

    $ python airflow_trigger.py get_dag_info

The list is sorted by the start date of the dag. The first item in the list is the latest start date. The script returns all information in this way.

The dag information contains the following:

* run_id
* dag_id
* start_date, end_date, duration
* execution_date
* state

With *---dag_id*, *---run_id* and *---last_n* the returns can be modified. For example::

    $ python airflow_trigger.py get_dag_info --dag_id feature_extraction

will return only the dags for the feature extraction. Adding *---last_n n* limits the return to information about the last n dags.

If the *run_id* of a dag is known the information for only that dag can be returned by using *---run_id*::

    $ python airflow_trigger.py get_dag_info --dag_id feature_extraction --run_id RUN_ID

NOTE: in the current version of the script the dag_id of the dag has to be specified for *---run_id* to work.

Running the following::

    $ python airflow_trigger get_dag_state

will return the state (running, success, failed) of the last dag that was started.
With *---run_id* the state of a specific dag can be returned.

Tasks
^^^^^

Similar to *get_dag_info*, *get_task_info* returns all tasks for all dags that have run::

    $ python airflow_trigger.py get_task_info

The task information contains the following:

* task_id
* dag_id
* start_date, end_date, duration
* execution_date
* state

Adding *---dag_id* or *---run_id* returns the all tasks that have run for the specified dags and *---last_n* limits the amount of information that is returned::

    $ python airflow_trigger.py get_task_info --dag_id feature_extraction --last_n 5
    $ python airflow_trigger.py get_task_info --run_id RUN_ID --last_n 5

With *---task_id* a task can be selected and than only information about those tasks will be returned::

    $ python airflow_trigger get_task_info --task_id get_video

This would return all tasks named *get_video* regardless of which dag it was started in.
Adding *---dag_id* or *---run_id* would restrict the return to the specified dag.

The supported tasks are for each of the dags are:

+-----------------------+-------------------------------------------------------------------------------------------------+
|shotdetection          |push_config_to_xcom, get_video, shotdetection                                                    |
+-----------------------+-------------------------------------------------------------------------------------------------+
|feature_extraction     |push_config_to_xcom, get_video, shotdetection, image_extraction, feature_extraction, update_index|
+-----------------------+-------------------------------------------------------------------------------------------------+
|aspect_ratio_extraction|push_config_to_xcom, get_video, shotdetection, image_extraction, aspect_ratio_extraction         |
+-----------------------+-------------------------------------------------------------------------------------------------+
|optical_flow           |push_config_to_xcom, get_video, optical_flow                                                     |
+-----------------------+-------------------------------------------------------------------------------------------------+

Logs
^^^^

The current version of the script doesn't support reading the log files of airflow.

To view the logs visit the airflow webserver at `<http://0.0.0.0:8080/>`_.

