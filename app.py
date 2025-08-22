import os
from flask import Flask, jsonify
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
    # This will stop the app if it can't connect, errors will be in Render logs
    raise

# --- Battery Configuration ---
# Adjust these values to match your specific 48V battery pack's specs
VOLTAGE_MAX = 54.6  # Voltage at 100% charge
VOLTAGE_MIN = 42.0  # Voltage at 0% charge

def calculate_soc(voltage):
    """Calculates the State of Charge (SOC) from voltage."""
    if voltage >= VOLTAGE_MAX:
        return 100
    if voltage <= VOLTAGE_MIN:
        return 0
    
    # Calculate percentage within the range
    percent = ((voltage - VOLTAGE_MIN) / (VOLTAGE_MAX - VOLTAGE_MIN)) * 100
    return round(percent)

# --- API Route ---
@app.route('/status')
def get_status():
    try:
        response = openapi.get(f"/v1.0/devices/{DEVICE_ID}/status")
        
        if response.get('success'):
            status_result = response['result']
            voltage_dp = next((item for item in status_result if item['code'] == 'cur_voltage'), None)

            if voltage_dp:
                # Normalize the voltage value (e.g., 5289 -> 52.89)
                current_voltage = voltage_dp['value'] / 100.0
                
                # Calculate the SOC
                soc = calculate_soc(current_voltage)

                return jsonify({
                    "soc": soc,
                    "voltage": round(current_voltage, 2)
                })
            else:
                return jsonify(error="Voltage data point ('cur_voltage') not found"), 404
        else:
            return jsonify(error="Failed to fetch data from Tuya API", details=response), 500
            
    except Exception as e:
        return jsonify(error="An internal server error occurred", details=str(e)), 500

@app.route('/health')
def health():
    return jsonify(status="ok")
