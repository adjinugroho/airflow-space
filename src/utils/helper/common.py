from airflow.models import Variable
from datetime import datetime
import pytz

from utils.constants.airflow.variable import AirflowVariable

localTz = pytz.timezone(Variable.get(AirflowVariable.LocalTZ))

class CommonHelper:
    def pytzLocalTz():
        return localTz

    def dtUtcToLocalISO(dtUtc: datetime | None):
        if dtUtc is None:
            return datetime.now(tz=localTz)
        else:
            return dtUtc.replace(tzinfo=pytz.utc).astimezone(localTz)
