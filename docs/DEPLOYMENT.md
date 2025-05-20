# Deployment Guide - Collaborative Event Management System

This guide provides instructions for deploying the Collaborative Event Management System in different environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Performance Tuning](#performance-tuning)
- [Monitoring](#monitoring)

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (for caching)
- Virtual environment tool (venv)

## Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd event-management
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database:
```bash
alembic upgrade head
```

6. Run development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Production Deployment

### Using Docker

1. Build the Docker image:
```bash
docker build -t event-management .
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

### Manual Deployment

1. Set up a production server with:
   - Nginx as reverse proxy
   - Gunicorn as WSGI server
   - Supervisor for process management

2. Install system dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-dev postgresql postgresql-contrib nginx
```

3. Create production environment:
```bash
python3 -m venv /opt/event-management
source /opt/event-management/bin/activate
pip install -r requirements.txt
```

4. Configure Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

5. Configure Supervisor:
```ini
[program:event-management]
command=/opt/event-management/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
directory=/opt/event-management
user=www-data
autostart=true
autorestart=true
```

## Environment Variables

Required environment variables:
```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
API_V1_PREFIX=/api/v1
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000"]
```

## Database Setup

1. Create database:
```sql
CREATE DATABASE event_management;
CREATE USER event_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE event_management TO event_user;
```

2. Run migrations:
```bash
alembic upgrade head
```

## Performance Tuning

### Database Optimization

1. Add indexes for frequently queried fields:
```sql
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_events_owner_id ON events(owner_id);
```

2. PostgreSQL configuration (postgresql.conf):
```
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 768MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 6553kB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Application Performance

1. Enable caching:
```python
# In app/core/config.py
REDIS_URL = "redis://localhost:6379/0"
CACHE_EXPIRE_TIME = 300  # 5 minutes
```

2. Configure Gunicorn:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --max-requests 1000
```

## Monitoring

1. Install monitoring tools:
```bash
pip install prometheus_client
pip install sentry-sdk
```

2. Configure logging:
```python
# In app/core/logging.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'level': 'WARNING',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

3. Set up health checks:
```bash
curl http://localhost:8000/health
```

## Backup and Recovery

1. Database backup:
```bash
pg_dump -U event_user event_management > backup.sql
```

2. Database restore:
```bash
psql -U event_user event_management < backup.sql
```

## Security Considerations

1. Enable SSL/TLS:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
}
```

2. Set security headers:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

Common issues and solutions:

1. Database connection issues:
   - Check PostgreSQL service status
   - Verify connection string
   - Check firewall settings

2. Performance issues:
   - Monitor database queries
   - Check cache hit ratio
   - Review application logs

3. Memory issues:
   - Adjust Gunicorn worker count
   - Monitor memory usage
   - Check for memory leaks

For more assistance, contact: support@example.com
