FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ ./app/
COPY assets/ ./assets/
COPY templates/ ./templates/
COPY config.py run.py ./

# Create instance directory for SQLite
RUN mkdir -p /app/instance && chmod 755 /app/instance

# Expose port
EXPOSE 6003

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:6003/')"

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:6003", "--workers", "2", "--threads", "2", "--timeout", "120", "run:app"]

