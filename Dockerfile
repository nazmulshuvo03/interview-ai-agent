# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11.6
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONUNBUFFERED=1

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Install build dependencies
RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set workdir and give appuser ownership
WORKDIR /home/appuser
COPY . .
RUN chown -R appuser:appuser /home/appuser
RUN chmod +r main.py

# Switch to non-root user
USER appuser

# Setup Python cache
RUN mkdir -p /home/appuser/.cache

# Install Python dependencies
RUN python -m pip install --user --no-cache-dir -r requirements.txt

# Download necessary models/files
RUN python main.py download-files

EXPOSE 8081

CMD ["python", "main.py", "start"]

