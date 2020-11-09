import requests
import json


def trigger_dag(dag_id, dag_configuration_json):
    dag_id = 'shotdetection'

    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }


    dag_configuration_json = '{"conf":"{\\"key\\":\\"value\\"}"}'

    dag_configuration_json = '{}'

    with open('variables.json') as j:
        data = json.load(j)
        for d in data:
            print(d)

    # p = json.dumps(dag_configuration_json)
    # print(p)
    # p = json.loads(p)
    # print(p)
    #
    # url = 'http://localhost:8080/api/experimental/dags/{dag_id}/dag_runs'.format(dag_id=dag_id)
    # response = requests.post(url, headers=headers, data=dag_configuration_json)
    # print(response)


if __name__ == '__main__':
    trigger_dag()
