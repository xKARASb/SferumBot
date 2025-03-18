FROM python:3.13-slim AS builder
ENV PIP_NO_CACHE_DIR=1
RUN apt-get update && \
    apt-get install -y --fix-missing --no-install-recommends git python3-dev gcc
RUN rm -rf /var/lib/apt/lists/ /var/cache/apt/archives/ /tmp/*
RUN git clone https://github.com/xKARASb/SferumBot.git /SferumBot
RUN python -m venv /venv
RUN /venv/bin/pip install --no-warn-script-location --no-cache-dir -r /SferumBot/requirements.txt
FROM python:3.13-slim
RUN rm -rf /var/lib/apt/lists/ /var/cache/apt/archives/ /tmp/*
ENV DOCKER=true \
    GIT_PYTHON_REFRESH=quiet \
    PIP_NO_CACHE_DIR=1
COPY --from=builder /SferumBot /SferumBot
COPY --from=builder /venv /SferumBot/venv

CMD ["python3", "startup.py"]