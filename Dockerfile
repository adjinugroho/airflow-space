FROM apache/airflow:2.8.0-python3.11

ENV TZ=Asia/Jakarta
ENV PYTHONPATH "${PYTHONPATH}:${AIRFLOW_HOME}"

RUN pip install markupsafe==2.0.1 \
    && pip install apache-airflow-providers-microsoft-mssql \
    && pip install apache-airflow-providers-odbc \
    && pip install pyodbc \
    && pip install connexion[swagger-ui]
