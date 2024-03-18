from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable, XCom
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.db import provide_session
from datetime import datetime, timedelta

from utils.constants.airflow.variable import AirflowVariable
from utils.helper.common import CommonHelper

import json

default_args = {
    "depends_on_past": False,
    "owner": "Adji Nugroho",
    "email": [Variable.get(AirflowVariable.ErrorEmailTo)],
    "email_on_failure": True,
    "email_on_retry": True,
    "start_date": datetime(2024, 3, 2, tzinfo=CommonHelper.pytzLocalTz()),
    "retries": 1,
    "retry_delay": timedelta(minutes=30),
}


@provide_session
def Cleanup(session=None, **context):
    dag = context["dag"]
    dag_id = dag._dag_id
    session.query(XCom).filter(XCom.dag_id == dag_id).delete()


with DAG(
    dag_id="Currency_FromUSD",
    default_args=default_args,
    schedule_interval="0 12 * * *",
    catchup=False,
) as dag:
    taskStart = EmptyOperator(task_id="Start")

    taskEnd = EmptyOperator(task_id="End")

    fetch_from_api = SimpleHttpOperator(
        task_id="FetchCurrency",
        http_conn_id="currency_api",
        endpoint="currency-api@latest/v1/currencies/usd.min.json",
        method="GET",
        do_xcom_push=True,
    )

    @task(task_id="SaveToDb")
    def SaveToDb(**kwargs):
        ti = kwargs["ti"]
        currData = ti.xcom_pull(key=None, task_ids="FetchCurrency")

        jsonData = json.loads(currData)

        hook = PostgresHook(postgres_conn_id="db_currency")
        conn  = hook.get_conn()
        cursor = conn .cursor()
        
        cursor.execute(f"SELECT * FROM currency WHERE date = '{jsonData['date']}'")
        if len(cursor) > 0:
            cursor.execute(
                f"UPDATE currency SET idr = {jsonData['usd']['idr']} WHERE date = '{jsonData['date']}'"
            )
        else:
            cursor.execute(
                f"INSERT INTO currency (date, idr) VALUES ('{jsonData['date']}', {jsonData['usd']['idr']})"
            )

        conn .commit()
        cursor.close()
        conn .close()

    cleanup = PythonOperator(
        task_id="CleanUp", python_callable=Cleanup, provide_context=True
    )

    taskStart >> fetch_from_api >> SaveToDb() >> cleanup >> taskEnd
