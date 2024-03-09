FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade gunicorn

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pnogo_api pnogo_api

CMD ["gunicorn", "-w 2", "-b :8080", "pnogo_api.run:app"]