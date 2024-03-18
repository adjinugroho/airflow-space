from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta

from utils.helper.variable import AirflowVariable
from utils.helper.common import CommonHelper

import json

default_args = {
    "depends_on_past": True,
    "owner": "Adji Nugroho",
    "email": [Variable.get(AirflowVariable.error_email)],
    "email_on_failure": True,
    "email_on_retry": True,
    "start_date": datetime(2024, 3, 2, tzinfo=CommonHelper.pytztz_local()),
    "retries": 1,
    "retry_delay": timedelta(minutes=30),
}


with DAG(
    dag_id="Currency_FromUSD",
    default_args=default_args,
    schedule_interval="0 12 * * *",
    catchup=True,
) as dag:
    task_start = EmptyOperator(task_id="Start")

    task_end = EmptyOperator(task_id="End")

    fetch_from_api = SimpleHttpOperator(
        task_id="FetchCurrency",
        http_conn_id="currency_api",
        endpoint="currency-api@{{ ds }}/v1/currencies/usd.min.json",
        method="GET",
        do_xcom_push=True,
    )

    @task(task_id="SaveToDb")
    def save_to_db(**kwargs):
        ti = kwargs["ti"]
        currData = ti.xcom_pull(key=None, task_ids="FetchCurrency")

        jsonData = json.loads(currData)

        hook = PostgresHook(postgres_conn_id="db_currency")
        conn = hook.get_conn()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM currency WHERE date = '{jsonData['date']}'")
        exists = cursor.fetchall()
        if len(exists) > 0:
            cursor.execute(
                f"UPDATE currency SET idr = {jsonData['usd']['idr']} WHERE date = '{jsonData['date']}'"
            )
        else:
            cursor.execute(
                f"INSERT INTO currency (date, idr) VALUES ('{jsonData['date']}', {jsonData['usd']['idr']})"
            )

        conn.commit()
        cursor.close()
        conn.close()

    task_start >> fetch_from_api >> save_to_db() >> task_end
