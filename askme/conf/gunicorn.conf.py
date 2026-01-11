import multiprocessing

# WSGI application
wsgi_app = "askme.wsgi:application"

# Server adres
bind = "127.0.0.1:8012"

# Workers configurations
workers = multiprocessing.cpu_count() * 2 + 1

# Logging
#accesslog = "logs/gunicorn/gunicorn.access.log"
#errorlog = "logs/gunicorn/gunicorn.error.log"

# def on_starting(server):
# 	pass

# def on_reload(server):
# 	pass

# def when_ready(server):
# 	pass
