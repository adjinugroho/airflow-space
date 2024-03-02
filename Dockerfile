FROM apache/airflow:2.8.2-python3.11

ENV TZ=Asia/Jakarta
ENV PYTHONPATH "${PYTHONPATH}:${AIRFLOW_HOME}"

RUN pip install markupsafe==2.0.1 \
    && pip install pyodbc \
    && pip install connexion[swagger-ui]
