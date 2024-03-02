from airflow.models import Variable
from datetime import datetime, timedelta

import logging
import os

from utils.constants.airflow.variable import AirflowVariable


class LogCleaner(object):
    def __init__(self, dateProc):
        super(LogCleaner, self).__init__()

        defLogCount = int(Variable.get(AirflowVariable.DefaultLogCount))

        self.dirAirflowLogs = "/opt/airflow/logs"
        self.dirAirflowProcManager = "/opt/airflow/logs/dag_processor_manager"
        self.logToRemoveDate = (dateProc - timedelta(days=defLogCount)).replace(
            tzinfo=None
        )

    def SchedulerLog(self):
        for dir in [
            f
            for f in os.scandir(self.dirAirflowLogs + "/scheduler")
            if f.is_dir(follow_symlinks=False)
        ]:
            logging.info(f"Found folder {dir.name} inside scheduler logs..")
            folderDate = datetime.strptime(dir.name, "%Y-%m-%d")

            if folderDate < self.logToRemoveDate:
                for root, dirs, files in os.walk(dir.path, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))

                os.rmdir(dir)

                logging.info(f"Scheduler log {dir.name} removed!")

    def ProcManagerLog(self):
        pass

    def DagLog(self):
        for dir in [
            f
            for f in os.scandir(self.dirAirflowLogs)
            if f.is_dir(follow_symlinks=False)
        ]:
            if dir.name.startswith("dag_id="):
                for dirDag in [
                    f for f in os.scandir(dir.path) if f.is_dir(follow_symlinks=False)
                ]:
                    logging.info(f"Found folder {dirDag.name} inside DAG logs..")

                    strIdx = dirDag.name.find("__") + 2
                    folderDate = datetime.strptime(
                        dirDag.name[strIdx : strIdx + 10], "%Y-%m-%d"
                    )

                    if folderDate < self.logToRemoveDate:
                        for root, dirs, files in os.walk(dirDag.path, topdown=False):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))

                        os.rmdir(dirDag)

                        logging.info(f"DAG log {dirDag.name} removed!")
