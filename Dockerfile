FROM quay.io/jupyter/all-spark-notebook:latest

USER root
# Install system dependencies required for building psycopg2 from source
# libpq-dev contains pg_config, gcc is for compilation
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt
