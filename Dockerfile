FROM apache/airflow:latest-python3.11

ENV TZ=Asia/Jakarta
ENV PYTHONPATH "${PYTHONPATH}:${AIRFLOW_HOME}"

RUN pip install --user --upgrade pip

# RUN pip install markupsafe==2.0.1 \
#     && pip install connexion[swagger-ui]
