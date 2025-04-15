FROM python:3.13.3-slim-bullseye

COPY . /app

WORKDIR /app

ARG EMBED_COL_NEW
ARG ALGO_TYPE
ARG SEC_KEY_NEW
ARG DB_NAME_NEW
ARG DB_URL_NEW
ARG USR_COL_NEW

ENV DB_URL_NEW=$DB_URL_NEW
ENV SEC_KEY_NEW=$SEC_KEY_NEW
ENV ALGO_TYPE=$ALGO_TYPE

ENV DB_NAME_NEW=$DB_NAME_NEW

ENV EMBED_COL_NEW=$EMBED_COL_NEW
ENV USR_COL_NEW=$USR_COL_NEW

RUN apt-get update
RUN apt-get install -y ffmpeg libsm6 libxext6
RUN pip install --verbose -r requirements.txt


CMD ["python", "main_entry.py"]

