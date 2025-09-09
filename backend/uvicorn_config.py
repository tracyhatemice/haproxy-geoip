# uvicorn configuration for production deployment
# Usage: uvicorn geoip_lookup:app --config uvicorn_config.py

import os

# Server configuration
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '6970')}"
workers = int(os.getenv('WORKERS', '4'))

# Performance tuning
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Logging
log_level = "info"
access_log = True
error_log = "-"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Keep alive
keepalive = 5
timeout = 30

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
