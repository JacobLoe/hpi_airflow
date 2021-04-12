.. _airflow:

Airflow
=======

Airflow is started with the following command::

    docker-compose -f docker-compose.yml up

If extracted features are to be used for the near duplicate detection *--network ada_subnet* has to be included.
The networks needs to be the same as the one for the server and client from the near duplicate detection.

In your browser go to `<http://0.0.0.0:8080/>`_ to get access to the airflow webserver.

Start an extractor
------------------

The different extractors are triggered with the *airflow_manager.py*. The script needs Python 3 installed. For example to start the shotdetection use the following command::

    python airflow_manager.py trigger_dag admin admin --dag_id shotdetection --run_id shotdetection_test0 --videoid 6ffaf51e5040724cd40c4411fcb872474b653710e9c88271ec98efe549c71e01

Choose with "--dag_id" which extractor is started. Use "--help" to get a list of the available extractors.
"--run_id" sets a unique id for a extractor which can be used to find it again. If the id was already used, the extractor cannot be started.

Whenever a extractor has run successfully a *.done-file* will be written which includes the date the extractor was last changed and the parameters that were used to run it.
If the same extractor is run again, the extraction for any results for which the content of the *.done-file* matches the parameters of the current extractor will be skipped.
Optionally each extractor (including the tasks *update_index* and *get_video*) has a parameter *force_run* which, if set to *True*, forces the extractor to run again regardless
of the *.done-file*.

*admin* *admin* are the username and password respectively and can be substituted by other credentials if the user has the appropriate permissions.

actions and arguments
----------------------

The airflow_manager script allows the following actions:

* trigger_dag
* get_available_dags
* get_last_run_state
* get_xcoms_per_dag
* get_xcom_values
* get_dag_doc
* list_dag_runs
* list_variables
* list_tasks
* delete_dag_runs_by_timestamp
* delete_dag_run

Each action is explained in the following sections.

The script takes the following arguments:

* --dag_id
* --dag_run_id
* --video_id
* --execution_date_gte
* --execution_date_lte
* --start_date_gte
* --start_date_lte
* --end_date_gte
* --end_date_lte
* --server_url

Not all arguments have functionality with all actions. All actions that return a list of dags/tasks can be modified with the date arguments to return info only from within the specified timeframe.
*start_date* specifies when a dag was triggered from the *UI* or the *airflow_manager*. *execution_date* specifies when a dag actually started. Depending on how many other dags are in the queue this can vary significantly from the *start_date*.
*end_date* signifies when a dag run has finished. *gte* and *lte* stand for *greater/less or equal*, meaning airflow searches for entries later or earlier than the date respectively.

*--dag_id* can also process multiple arguments, for example like *--dag_id shotdetection deepfeatures'. Then the script would search for the latest shotdetection or deepfeatures dag.
This does not work with *trigger_dag*, *get_dag_doc*, *get_xcoms_per_dag*, *get_xcom_values*, *list_tasks* and *delete_dag_run*. These actions will work with multiple dag ids but will only process the first entry of the list.

Finally *--sever_url* has *http://0.0.0.0:8080* as its default address for the airflow server.

Get information about an extractor
----------------------------------

The *airflow_manager.py* can also be used to get information about any graphs or tasks that are/were running. The commands only works if the airflow webserver is running.

DAGs
^^^^

Use the following command to get a list of all dags that are available on the airflow server run::

    python get_available_dags admin admin

The list contains a list of dictionaries containing the the dag id and a short description of the dag.
To get a more detailed description of a dag use::

    python airflow_manager.py get_dag_doc admin admin --dag_id shotdetection

Use the following command to get the last dag that has run for a particular videoid::

    python airflow_manager.py get_last_run_state admin admin --dag_id deepfeatures --videoid 6ffaf51e5040724cd40c4411fcb872474b653710e9c88271ec98efe549c71e01

Here the script would return the last deepfeatures dag that has run for the videoid.

The list is sorted by the execution date of the dag. The first item in the list is the latest executed date. The script returns all information in this way.
The dag information contains the following:

* dag_run_id
* dag_id
* execution_date
* state
* xcoms per task

With *list_dag_runs* you'll get information about all dags that have run in the specified timeframe. For example::

    python airflow_manager.py list_dag_runs admin admin --dag_id shotdetection deepfeatures --start_date_gte 2021-03-24T14:24:00Z

By adding *--video_id* the list can be restricted only to dags that have run for the specified videoid.
The information contains the following:

* dag_run_id
* dag_id
* configuration
* state
* execution_date, start_date, end_date

Miscellaneous
^^^^^^^^^^^^^

*list_tasks* list all tasks for a dag::

    python airflow_manager.py list_tasks admin admin --dag_id shotdetection --dag_run_id test

It returns only the name of the tasks.

With *get_xcom_values* one can get all xcoms and their values for a dag run::

    python airflow_manager.py get_xcom_values admin admin --dag_id shotdetection --dag_run_id test

Each entry contains the *task id* and the name of the xcom as the key and their corresponding value.

*list_variables* lists all variables used by airflow::

    python airflow_manager.py list_variables admin admin


With *delete_dag_run* one can delete single dag runs from the airflow server::

    python airflow_manager.py delete_dag_run admin admin --dag_id shotdetection --dag_run_id test

With *delete_dag_runs_by_time* multiple dag runs can be deleted at once.

    python airflow_manager.py delete_dag_run admin admin --dag_id shotdetection --dag_run_id test --start_date_gte 2021-03-24T14:24:00Z
