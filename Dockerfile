FROM python:3.10.1-slim

ENV CONTAINER_HOME=/usr/src/www

ADD . $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

RUN pip install -r $CONTAINER_HOME/requirements.txt
