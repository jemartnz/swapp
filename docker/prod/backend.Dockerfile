FROM python:3.13-alpine AS builder

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libpq-dev

COPY back/requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-alpine

WORKDIR /app

RUN apk add --no-cache libpq

COPY --from=builder /install /usr/local

COPY back/ ./back/

EXPOSE 5000

CMD ["gunicorn", "back.wsgi:app", "--bind", "0.0.0.0:5000", "--workers", "4"]
