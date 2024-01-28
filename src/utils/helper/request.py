from airflow.exceptions import AirflowException
import json
import requests

class RequestJsonHelper(object):
    def __init__(self, headers):
        self.RequestHeader = headers

    def Get(self, url, params=None):
        try:
            response = requests.get(
                url=url,
                headers=self.RequestHeader,
                params=params
            )
            response.raise_for_status()

            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except requests.exceptions.HTTPError as err:
            raise AirflowException("Request error: " + err.response.text)

    def Post(self, url, data):
        try:
            response = requests.post(
                url=url,
                headers=self.RequestHeader,
                data=json.dumps(data) if bool(data) else None,
            )
            response.raise_for_status()

            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except requests.exceptions.HTTPError as err:
            raise AirflowException("Request error: " + err.response.text)

    def Put(self, url, data):
        try:
            response = requests.put(
                url=url,
                headers=self.RequestHeader,
                data=json.dumps(data),
            )
            response.raise_for_status()

            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except requests.exceptions.HTTPError as err:
            raise AirflowException("Request error: " + err.response.text)
