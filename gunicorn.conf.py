# Gunicorn configuration file

# Define the address and port for the server to listen on
bind = "0.0.0.0:8000"

# Number of worker processes
workers = 2

# Worker class for handling requests
worker_class = "gthread"

# Number of threads for handling requests (if using a threaded worker class)
threads = 4

# Worker timeout 30s
timeout = 30

# Maximum requests a worker will process before restarting
max_requests = 1000

# # Access log file
# accesslog = '/var/log/gunicorn/access.log'

# # Error log file
# errorlog = '/var/log/gunicorn/error.log'

# Log level
loglevel = "debug"
