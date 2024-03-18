from airflow.models import Variable
from datetime import datetime
import pytz

from utils.helper.variable import AirflowVariable

tz_local = pytz.timezone(Variable.get(AirflowVariable.tz_local))

class CommonHelper:
    def pytztz_local():
        return tz_local

    def dtUtcToLocalISO(dtUtc: datetime | None):
        if dtUtc is None:
            return datetime.now(tz=tz_local)
        else:
            return dtUtc.replace(tzinfo=pytz.utc).astimezone(tz_local)
