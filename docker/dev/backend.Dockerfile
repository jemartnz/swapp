FROM python:3.13-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libpq-dev

COPY back/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY back/ ./back/

EXPOSE 5000
