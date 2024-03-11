FROM apache/airflow:latest-python3.11

ENV TZ=Asia/Jakarta
ENV PYTHONPATH "${PYTHONPATH}:${AIRFLOW_HOME}"

RUN pip install --user --upgrade pip

RUN pip install markupsafe \
    && pip install connexion[swagger-ui]
