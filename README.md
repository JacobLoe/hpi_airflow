1: install airflow version 1.10.12
https://airflow.apache.org/docs/stable/installation.html

2: run airflow in terminal with 'airflow' to create an folder for logs and configuration at ~/airflow

3: go to the new folder and open airflow.cfg

    change "dags_folder" to the directoy of the repository. The path has to be absolute
    change "load_examples" to False (not strictly necessary, but removes clutter)
    
4: execute "airflow initdb" in terminal to add the DAG in the repository to airflow

5: execute "airflow webserver -p 8080" in the terminal, then "http://0.0.0.0:8080/" in the browser to track the progess of the DAG visually

6: execute "airflow scheduler" in the terminal to start the DAG
