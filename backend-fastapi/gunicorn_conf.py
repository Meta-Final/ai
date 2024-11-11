# gunicorn_conf.py
workers_per_core = 1
cores = 6
workers = workers_per_core * cores
threads = 2
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
keepalive = 120
errorlog = "-"
accesslog = "-"
loglevel = "info"