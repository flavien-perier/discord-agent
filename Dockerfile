FROM python:3.15-rc-alpine

WORKDIR /app

COPY requirements.txt .
RUN apk add --no-cache gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev

COPY src/ ./src/

CMD ["python", "-m", "src.main"]
