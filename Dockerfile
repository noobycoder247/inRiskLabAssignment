FROM python:3.7-alpine

# Set working directory
WORKDIR /app


# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create the weather_data directory
RUN mkdir -p weather_data


# Expose the port that Cloud Run expects
EXPOSE 8080

# Run the application
CMD ["gunicorn", "--bind", "0.0.0:8080", "app:app"]