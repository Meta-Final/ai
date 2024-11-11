FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /workspace
RUN mkdir -p /workspace/app
RUN mkdir -p /workspace/storage
RUN mkdir -p /workspace/generated


COPY ./backend-fastapi/gunicorn_conf.py .
COPY main.py .

ENTRYPOINT [ "gunicorn", "main:app", "-c", "gunicorn_conf.py" ]