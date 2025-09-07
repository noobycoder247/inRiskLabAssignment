import json
import os.path
import traceback

import requests
from flask import Flask, jsonify, request

from constants import LOCAL_FOLDER_NAME, BUCKET_NAME, BUCKET_FOLDER_NAME
from storage_helper import BucketHelper

app = Flask(__name__)

abs_path = os.path.dirname(os.path.abspath(__file__))

# For Cloud Run deployment, authentication is handled by the service account
# attached to the Cloud Run service. No need to set GOOGLE_APPLICATION_CREDENTIALS
# when running in Cloud Run environment.
if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    # Only set credentials for local development
    credentials_path = os.path.join(abs_path, 'credentials.json')
    if os.path.exists(credentials_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

if not os.path.exists(os.path.join(abs_path, LOCAL_FOLDER_NAME)):
    os.mkdir(os.path.join(abs_path, LOCAL_FOLDER_NAME))


@app.route('/', methods=['GET'])
def home():
    return jsonify({'msg': 'Everything looks healthy!'})


@app.route('/store-weather-data', methods=['POST'])
def store_weather_data():
    request_data = request.get_json()
    required_input_fields = ['latitude', 'longitude', 'start_date', 'end_date']
    for required_input_field in required_input_fields:
        if required_input_field not in request_data:
            return jsonify({'error': f'{required_input_field} is required'}), 400

    latitude = request_data['latitude']
    longitude = request_data['longitude']
    start_date = request_data['start_date']
    end_date = request_data['end_date']
    weather_data_variables = ['temperature_2m_max', 'temperature_2m_min', 'temperature_2m_mean',
                              'apparent_temperature_max', 'apparent_temperature_min', 'apparent_temperature_mean']
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start_date,
        'end_date': end_date,
        'daily': ','.join(weather_data_variables)
    }
    url = f'https://archive-api.open-meteo.com/v1/archive'
    try:
        response = requests.get(url, params)
        response.raise_for_status()
        weather_data = response.json()
        for field in ['daily', 'daily_units']:
            if field not in weather_data:
                return jsonify({'error': f'Unexpected weather API response format, {field} field not present'}), 500
        for field in weather_data_variables:
            if field not in weather_data['daily']:
                return jsonify({'error': f'Unexpected weather API response format, {field} field not present'}), 500

        created_files = []
        created_files_path = []
        for weather_data_variable in weather_data_variables:
            collected_data = {}
            unit = weather_data['daily_units'][weather_data_variable]
            for time, data in zip(weather_data['daily']['time'], weather_data['daily'][weather_data_variable]):
                collected_data[time] = f'{data}{unit}'
            filename = f'{weather_data_variable}.json'
            full_path = os.path.join(abs_path, LOCAL_FOLDER_NAME, filename)

            with open(full_path, 'w') as f:
                json.dump(collected_data, f, indent=4)
                created_files.append(filename)
                created_files_path.append(full_path)

        bucket_helper = BucketHelper(BUCKET_NAME)
        for created_file in created_files:
            local_file_path = os.path.join(abs_path, LOCAL_FOLDER_NAME, created_file)
            cloud_file_path = BUCKET_FOLDER_NAME + '/' + created_file
            bucket_helper.upload_file(local_file_path, cloud_file_path)

        # clean up local files
        for created_file_path in created_files_path:
            if os.path.exists(created_file_path):
                os.remove(created_file_path)

        return jsonify({'msg': 'Fetched and stored weather data successfully', 'created_files': created_files}), 201
    except requests.exceptions.HTTPError as err:
        status_code = err.response.status_code if err.response else 500
        return jsonify({
            'error': f'Weather API error: {err.response.text if err.response else str(err)}'
        }), status_code
    except Exception as err:
        print(traceback.print_exc())
        return jsonify({'error': f'Unexpected error: {str(err)}'}), 500


@app.route('/list-weather-files', methods=["GET"])
def list_weather_files():
    bucket_helper = BucketHelper(BUCKET_NAME)
    weather_files = []
    for filename in bucket_helper.list_files(BUCKET_FOLDER_NAME):
        weather_files.append(os.path.basename(filename))

    return jsonify({'msg': 'Listed files successfully', 'file_list': weather_files}), 200


@app.route('/weather-file-content/<string:filename>', methods=['GET'])
def weather_file_content(filename):
    bucket_helper = BucketHelper(BUCKET_NAME)
    cloud_file_path = "/".join([BUCKET_FOLDER_NAME, filename])
    if not bucket_helper.file_exists(cloud_file_path):
        return jsonify({'error': f'{filename} does not exist'}), 404

    file_content = bucket_helper.read_json(cloud_file_path)
    return jsonify({'msg': 'Content fetched successfully', 'content': file_content, 'filename': filename}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
