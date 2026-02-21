FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Google Standard: Rootless Execution ---
RUN useradd -m -u 10001 honeypot
RUN mkdir -p /app/data /app/logs /app/quarantine && \
    chown -R honeypot:honeypot /app

# Copy project files
COPY --chown=honeypot:honeypot . .

# Expose ports
# 2121: FTP, 2222: SSH, 8000: Prometheus Metrics
EXPOSE 2121 2222 8000

# Create volume for logs and persistence
VOLUME ["/app/logs", "/app/data", "/app/quarantine"]

# Run as non-root user
USER honeypot

# Run the honeypot
CMD ["python", "rabbithole.py"]
