FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install zip
WORKDIR /server

COPY ./server/requirements.txt .
RUN pip install -r requirements.txt

COPY ./server /server/
