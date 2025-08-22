import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from tuya_connector import TuyaOpenAPI

# --- Setup is the same ---
log_file = os.path.join(os.path.dirname(__file__), 'app.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

app = Flask(__name__)
CORS(app)
logging.info("Flask app created.")

try:
    ACCESS_ID = os.environ.get('TUYA_ACCESS_ID')
    ACCESS_KEY = os.environ.get('TUYA_ACCESS_KEY')
    API_ENDPOINT = "https://openapi.tuyaus.com"
    DEVICE_ID = os.environ.get('TUYA_DEVICE_ID')
    openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
    openapi.connect()
    logging.info("Successfully connected to Tuya API.")
except Exception as e:
    logging.error(f"CRITICAL: Failed during Tuya setup. Error: {e}", exc_info=True)

# --- NEW DEBUG ROUTE ---
@app.route('/debug')
def debug_device_status():
    """Fetches and returns the entire raw status response from Tuya."""
    try:
        # Get all status data points for the device
        response = openapi.get(f"/v1.0/devices/{DEVICE_ID}/status")
        # Return the entire response as JSON so you can see it in your browser
        return jsonify(response)
    except Exception as e:
        return jsonify(error=str(e))

# --- Your existing routes ---
@app.route('/soc')
def get_soc():
    # ... (your existing soc code)
    return jsonify(error="This is the old endpoint. Please use /debug for now.")

@app.route('/health')
def health():
    return jsonify(status="ok")
