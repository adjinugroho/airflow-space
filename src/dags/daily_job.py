from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

from controllers.log_cleaner import LogCleaner
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
    dag_id="Daily_Job",
    default_args=default_args,
    schedule_interval="0 6 * * *",
    catchup=False,
) as dag:
    logCleaner = LogCleaner(CommonHelper.dtUtcToLocalISO(dag.get_latest_execution_date()))

    taskStart = EmptyOperator(task_id="Start")

    taskEnd = EmptyOperator(task_id="End")

    with TaskGroup(group_id="LogCleaning") as tgLogCleaning:
        @task(task_id="CleanSchedulerLog")
        def CleanSchedulerLog():
            logCleaner.SchedulerLog()

        @task(task_id="CleanDagLog")
        def CleanDagLog():
            logCleaner.DagLog()

        @task(task_id="CleanProcManagerLog")
        def CleanProcManagerLog():
            logCleaner.ProcManagerLog()

        CleanSchedulerLog()
        CleanProcManagerLog()
        CleanDagLog()

    (
        taskStart
        >> tgLogCleaning
        >> taskEnd
    )
