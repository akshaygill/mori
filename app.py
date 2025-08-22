import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from tuya_connector import TuyaOpenAPI

# --- Create the Flask App ---
app = Flask(__name__)
CORS(app)

# --- Tuya Setup ---
try:
    ACCESS_ID = os.environ.get('TUYA_ACCESS_ID')
    ACCESS_KEY = os.environ.get('TUYA_ACCESS_KEY')
    DEVICE_ID = os.environ.get('TUYA_DEVICE_ID')
    API_ENDPOINT = "https://openapi.tuyaus.com"
    openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
    openapi.connect()
except Exception as e:
    raise

# --- Battery Configuration ---
VOLTAGE_MAX = 54.6
VOLTAGE_MIN = 42.0

def calculate_soc(voltage):
    if voltage >= VOLTAGE_MAX:
        return 100
    if voltage <= VOLTAGE_MIN:
        return 0
    percent = ((voltage - VOLTAGE_MIN) / (VOLTAGE_MAX - VOLTAGE_MIN)) * 100
    return round(percent)

# --- Route to Serve the Webpage ---
@app.route('/')
def home():
    """Serves the index.html file from the templates folder."""
    return render_template('index.html')

# --- API Route ---
@app.route('/status')
def get_status():
    try:
        response = openapi.get(f"/v1.0/devices/{DEVICE_ID}/status")
        if response.get('success'):
            status_result = response['result']
            voltage_dp = next((item for item in status_result if item['code'] == 'cur_voltage'), None)
            if voltage_dp:
                current_voltage = voltage_dp['value'] / 100.0
                soc = calculate_soc(current_voltage)
                return jsonify({"soc": soc, "voltage": round(current_voltage, 2)})
            else:
                return jsonify(error="Voltage data point ('cur_voltage') not found"), 404
        else:
            return jsonify(error="Failed to fetch data from Tuya API", details=response), 500
    except Exception as e:
        return jsonify(error="An internal server error occurred", details=str(e)), 500

@app.route('/health')
def health():
    return jsonify(status="ok")
