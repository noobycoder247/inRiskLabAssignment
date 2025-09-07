# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create the weather_data directory
RUN mkdir -p weather_data

# Set environment variables
ENV PORT=8080
ENV FLASK_APP=app.py

# Expose the port that Cloud Run expects
EXPOSE 8080

# Run the application
CMD ["python", "/app/app.py"]
