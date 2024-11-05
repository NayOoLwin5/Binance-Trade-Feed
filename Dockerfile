FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY .env .

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "src.main"]