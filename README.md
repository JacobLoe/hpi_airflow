1. build the airflow docker image with: "docker build -f Dockerfile_airflow -t jacobloe/airflow:0.1 ."
2. the image is started with:  
"docker run --rm -it -v $(pwd)/PATH_TO_DATA:/data -v /var/run/docker.sock:/var/run/docker.sock -p 8080:8080 --name airflow --entrypoint /bin/bash jacobloe/airflow:0.1"
3. in the container run "airflow scheduler & airflow webserver -p 8080" to start airflow 
4. outside of the container use "python airflow_trigger" to start a shotdetection graph
5. visit "http://0.0.0.0:8080/" in your browser to see the progress of the DAG
6. use "Graph View" to view progress of the graph during runtime
    
    6.1 click on a task and then on "View Log" to see the terminal output of a task