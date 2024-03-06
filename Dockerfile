FROM python:3.10-slim

WORKDIR /app

RUN pip install --upgrade gunicorn

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pnogo_api pnogo_api

CMD ["gunicorn", "-w 2", "-b :8080", "pnogo_api.run:app"]