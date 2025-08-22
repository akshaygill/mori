# app.py
from flask import Flask, jsonify
from tuya_connector import TuyaOpenAPI
import os

# --- Configuration ---
ACCESS_ID = os.environ.get('TUYA_ACCESS_ID')  # From Tuya IoT Platform
ACCESS_KEY = os.environ.get('TUYA_ACCESS_KEY')c # From Tuya IoT Platform
API_ENDPOINT = "https://openapi.tuyaus.com" # Or your region's endpoint
DEVICE_ID = os.environ.get('TUYA_DEVICE_ID') # Find this in the Tuya IoT Platform

# --- Flask App ---
app = Flask(__name__)

# --- Tuya Connection ---
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

@app.route('/api/soc')
def get_soc():
    # Get all status data points for the device
    response = openapi.get(f"/v1.0/devices/{DEVICE_ID}/status")

    # Check if the API call was successful
    if response.get('success'):
        # Find the battery percentage DP. The name might be 'battery_percentage', 'battery_state', etc.
        # You may need to check your device's DP list in the Tuya platform.
        battery_dp = next((item for item in response['result'] if item['code'] == 'battery_percentage'), None)

        if battery_dp:
            soc = battery_dp['value']
            return jsonify(soc=soc)
        else:
            return jsonify(error="Battery DP not found"), 404
    else:
        return jsonify(error="Failed to fetch data from Tuya API"), 500

if __name__ == '__main__':

    app.run(debug=True)
