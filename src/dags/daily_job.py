from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable, XCom
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

from controllers.daily_job import DailyJobTasks
from utils.helper.variable import AirflowVariable
from utils.helper.common import CommonHelper

default_args = {
    "depends_on_past": False,
    "owner": "Adji Nugroho",
    "email": [Variable.get(AirflowVariable.error_email)],
    "email_on_failure": True,
    "email_on_retry": True,
    "start_date": datetime(2024, 1, 1, tzinfo=CommonHelper.pytztz_local()),
    "retries": 1,
    "retry_delay": timedelta(minutes=30),
}

with DAG(
    dag_id="Daily_Job",
    default_args=default_args,
    schedule_interval="0 6 * * *",
    catchup=False,
) as dag:
    logCleaner = DailyJobTasks(
        CommonHelper.dtUtcToLocalISO(dag.get_latest_execution_date())
    )

    task_start = EmptyOperator(task_id="Start")

    task_end = EmptyOperator(task_id="End")

    with TaskGroup(group_id="log_cleaning") as tg_log_cleaning:

        @task(task_id="scheduler_log")
        def scheduler_log():
            logCleaner.scheduler_log()

        @task(task_id="dag_log")
        def dag_log():
            logCleaner.dag_log()

        @task(task_id="proc_manager_log")
        def proc_manager_log():
            logCleaner.proc_manager_log()

        scheduler_log()
        proc_manager_log()
        dag_log()

    with TaskGroup(group_id="misc_cleanup") as tg_misc_cleanup:

        @task(task_id="xcom")
        def xcom_data():
            logCleaner.xcom_cleanup()

        xcom_data()

    task_start >> [tg_log_cleaning, tg_misc_cleanup] >> task_end
