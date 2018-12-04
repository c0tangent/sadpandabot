FROM python:3.6.7-alpine3.8

WORKDIR /app
COPY requirements.txt /app/requirements.txt

# build dependencies
RUN \
    apk add --update --no-cache --virtual=build-deps \
    ca-certificates \
    g++ \
    gcc \
    git \
    linux-headers \
    make && \
    # runtime dependencies
    # pip packages
    pip install --no-cache-dir -U \
    pip && \
    pip install --no-cache-dir -r \
    requirements.txt && \
    # cleanup
    apk del --purge \
    build-deps && \
    rm -rf \
    /tmp/*

COPY . /app/
CMD ["python", "-u", "sadpandabot.py"]

