# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    ghostscript \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend-python/requirements.txt ./backend-python/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend-python/requirements.txt

# Copy the rest of the application
COPY backend-python ./backend-python

# Create necessary directories
RUN mkdir -p backend-python/uploads backend-python/outputs backend-python/logs

# Expose port (Railway will override with $PORT)
EXPOSE 8080

# Change to backend directory and start the application
WORKDIR /app/backend-python
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
