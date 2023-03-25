FROM jupyter/pyspark-notebook:spark-3.3.0

USER root
WORKDIR /code
COPY . /code

RUN apt-get update && apt-get install cron -y -qq
RUN touch /var/log/cron.log

RUN pip install --no-cache-dir kafka-python pyspark

ADD ./crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
CMD cron && tail -f /var/log/cron.log