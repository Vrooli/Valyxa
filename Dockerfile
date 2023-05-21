FROM python:3.9-alpine

ARG PROJECT_DIR
ARG VIRTUAL_PORT
WORKDIR ${PROJECT_DIR}

COPY requirements.txt .
COPY . .

# Install build dependencies, build the Python packages, and remove build dependencies to reduce image size
RUN apk add --no-cache --virtual .build-deps \
    bash \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

EXPOSE ${VIRTUAL_PORT}
