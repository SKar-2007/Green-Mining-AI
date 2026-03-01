# docker/Dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies (minimal; OpenCV may work without GUI libs)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create directories
RUN mkdir -p backend/uploads backend/results backend/models

EXPOSE 5000

CMD ["python", "backend/app.py"]
