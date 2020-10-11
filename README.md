1: install airflow version 1.10.12
https://airflow.apache.org/docs/stable/installation.html

2: run airflow in terminal with 'airflow' to create an folder for logs and configuration at ~/airflow

3: go to the new folder and open airflow.cfg

    change "dags_folder" to the directoy of the repository. The path has to be absolute
    change "load_examples" to False (not strictly necessary, but removes clutter in the ui)
    
4: execute "airflow webserver -p 8080" in the terminal, then "http://0.0.0.0:8080/" in the browser to track the progess of the DAG visually

5: execute "airflow scheduler" in the terminal

6: on the webserver under "http://0.0.0.0:8080/variable/list/" import the "variables.json"

7: to start the graph use the button "Trigger DAG" on the home screen

8: use "Graph View" to view progress of the graph during runtime