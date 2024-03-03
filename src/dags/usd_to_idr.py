from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

from utils.constants.airflow.variable import AirflowVariable
from utils.helper.common import CommonHelper

default_args = {
    "depends_on_past": False,
    "owner": "Adji Nugroho",
    "email": [Variable.get(AirflowVariable.ErrorEmailTo)],
    "email_on_failure": True,
    "email_on_retry": True,
    "start_date": datetime(2024, 1, 1, tzinfo=CommonHelper.pytzLocalTz()),
    "retries": 1,
    "retry_delay": timedelta(minutes=30),
}

with DAG(
    dag_id="Currency_USDtoIDR",
    default_args=default_args,
    schedule_interval="0 12 * * *",
    catchup=False,
) as dag:
    taskStart = EmptyOperator(task_id="Start")

    taskEnd = EmptyOperator(task_id="End")

    @task(task_id="FetchFromAPI")
    def FetchFromAPI():
        pass

    taskStart >> FetchFromAPI() >> taskEnd
