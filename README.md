1: install airflow version 1.10.12
https://airflow.apache.org/docs/stable/installation.html
    
    1.1 run "pip3 install docker" for the docker_operator.py
    
2: run airflow in terminal with 'airflow' to create an folder for logs and configuration at ~/airflow

3: go to the new folder and open airflow.cfg

    change "dags_folder" to the directoy of the repository. The path has to be absolute
    change "load_examples" to False (not strictly necessary, but removes clutter in the ui)

4: run "airflow initdb" to add the graph to the airflow database
    
5: execute "airflow webserver -p 8080" in the terminal, then "http://0.0.0.0:8080/" in the browser to track the progess of the DAG visually

6: execute "airflow scheduler" in the terminal

7: on the webserver under "http://0.0.0.0:8080/variable/list/" import the "variables.json"

8: to start the graph use the button "Trigger DAG" on the home screen

9: use "Graph View" to view progress of the graph during runtime