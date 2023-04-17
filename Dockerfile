FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

# Install build dependencies, build the Python packages, and remove build dependencies to reduce image size
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY . .

CMD ["python", "src/app.py"]
