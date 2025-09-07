# Weather Data API

A Flask-based REST API that fetches historical weather data from Open-Meteo API and stores it in Google Cloud Storage. The application is containerized with Docker and deployed on Google Cloud Run.

## Features

- Fetch historical weather data for specific coordinates and date ranges
- Store weather data in Google Cloud Storage
- List stored weather files
- Retrieve weather file content
- RESTful API endpoints
- Docker containerization
- Google Cloud Run deployment

## Setup and Installation

### Prerequisites

- Python 3.7+
- Google Cloud SDK
- Docker
- Google Cloud Project with the following APIs enabled:
  - Cloud Storage API
  - Artifact Registry API
  - Cloud Run API

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd assignment01
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Cloud credentials:**
   - Download your service account key file from Google Cloud Console
   - Place it as `credentials.json` in the project root
   - Set the environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
     ```

5. **Configure constants:**
   - Update `constants.py` with your Google Cloud Storage bucket name
   - Ensure the bucket exists in your GCP project

6. **Run the application locally:**
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:8080`

## Deployment to Google Cloud Run

### 0. Setup Storage Bucket
- Create Bucket with name 'sandip_test_bucket'
- Create new role with appropriate storage permissions
- Create Service Account and attach created role into it
- Download credential json file

### 1. Build and Push Docker Image to Artifact Registry

```bash
# Configure Docker authentication
gcloud auth configure-docker asia-south2-docker.pkg.dev

# Build the Docker image
docker build -t asia-south2-docker.pkg.dev/propane-forge-362006/flaskapp/weather-app:latest .

# Push to Artifact Registry
docker push asia-south2-docker.pkg.dev/propane-forge-362006/flaskapp/weather-app:latest
```

### 2. Deploy to Cloud Run

```bash
# Deploy the service
gcloud run deploy weather-api \
  --image asia-south2-docker.pkg.dev/propane-forge-362006/flaskapp/weather-app:latest \
  --platform managed \
  --region asia-south2 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10
```


## API Endpoints

### You can check out API [Postman Collection](./InRiskAssignment.postman_collection.json) as well.

### Base URL
```
https://weather-app-219248527136.europe-west1.run.app/
```

### 1. Health Check
- **Endpoint:** `GET /`
- **Description:** Returns a simple health check message
- **Response:**
  ```json
  {
    "msg": "Everything looks healthy!"
  }
  ```

### 2. Store Weather Data
- **Endpoint:** `POST /store-weather-data`
- **Description:** Fetches historical weather data and stores it in Google Cloud Storage
- **Request Body:**
  ```json
  {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "start_date": "2023-01-01",
    "end_date": "2023-01-31"
  }
  ```
- **Required Fields:**
  - `latitude` (float): Latitude coordinate
  - `longitude` (float): Longitude coordinate
  - `start_date` (string): Start date in YYYY-MM-DD format
  - `end_date` (string): End date in YYYY-MM-DD format

- **Response (Success - 201):**
  ```json
  {
    "msg": "Fetched and stored weather data successfully",
    "created_files": [
      "temperature_2m_max.json",
      "temperature_2m_min.json",
      "temperature_2m_mean.json",
      "apparent_temperature_max.json",
      "apparent_temperature_min.json",
      "apparent_temperature_mean.json"
    ]
  }
  ```

- **Response (Error - 400):**
  ```json
  {
    "error": "latitude is required"
  }
  ```

### 3. List Weather Files
- **Endpoint:** `GET /list-weather-files`
- **Description:** Lists all weather data files stored in Google Cloud Storage
- **Response:**
  ```json
  {
    "msg": "Listed files successfully",
    "file_list": [
      "temperature_2m_max.json",
      "temperature_2m_min.json",
      "temperature_2m_mean.json"
    ]
  }
  ```

### 4. Get Weather File Content
- **Endpoint:** `GET /weather-file-content/<filename>`
- **Description:** Retrieves the content of a specific weather data file
- **Path Parameters:**
  - `filename` (string): Name of the weather data file with extension

- **Response (Success - 200):**
  ```json
  {
    "msg": "Content fetched successfully",
    "content": {
      "2023-01-01": "5.2°C",
      "2023-01-02": "6.1°C",
      "2023-01-03": "4.8°C"
    },
    "filename": "temperature_2m_max.json"
  }
  ```

- **Response (Error - 404):**
  ```json
  {
    "error": "temperature_2m_max.json does not exist"
  }
  ```

## Weather Data Variables

The API fetches the following weather variables:
- `temperature_2m_max`: Maximum temperature at 2 meters
- `temperature_2m_min`: Minimum temperature at 2 meters
- `temperature_2m_mean`: Mean temperature at 2 meters
- `apparent_temperature_max`: Maximum apparent temperature
- `apparent_temperature_min`: Minimum apparent temperature
- `apparent_temperature_mean`: Mean apparent temperature

## Error Handling

The API includes comprehensive error handling for:
- Missing required fields (400 Bad Request)
- Invalid API responses (500 Internal Server Error)
- File not found (404 Not Found)
- Weather API errors (various HTTP status codes)

## Project Structure

```
assignment01/
├── app.py                 # Main Flask application
├── constants.py           # Configuration constants
├── storage_helper.py      # Google Cloud Storage helper class
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .dockerignore         # Docker ignore file
├── README.md             # This file
└── weather_data/         # Local storage directory (created at runtime)
```

## Dependencies

- Flask 2.2.5
- Google Cloud Storage 3.3.1
- Requests 2.31.0
- Gunicorn 23.0.0

## Live Demo

**Deployed Application URL:** `https://weather-app-219248527136.europe-west1.run.app/`

The application is deployed on Google Cloud Run and accessible publicly. You can test the API endpoints using the provided URLs and request formats above.

## Testing the API

You can test the API using curl or any HTTP client:

## Health check
```bash
curl https://weather-app-219248527136.europe-west1.run.app/
```

## Store weather data
```bash
curl -X POST https://weather-app-219248527136.europe-west1.run.app/store-weather-data \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "start_date": "2023-01-01",
    "end_date": "2023-01-31"
  }'
```

## List weather files
```bash
curl https://weather-app-219248527136.europe-west1.run.app/list-weather-files
```

## Get weather file content
```bash
curl https://weather-app-219248527136.europe-west1.run.app/weather-file-content/temperature_2m_max.json
```
