FROM python:3.13-slim

ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m venv /venv \
    && /venv/bin/pip install --no-warn-script-location --no-cache-dir -r requirements.txt

COPY . .

ENV PATH="/venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1

CMD ["python", "run_bot_background.py"]
