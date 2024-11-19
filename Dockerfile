FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install -y gcc \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN chmod +x /app/start.sh