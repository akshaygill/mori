import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from tuya_connector import TuyaOpenAPI

# --- Setup Logging ---
log_file = os.path.join(os.path.dirname(__file__), 'app.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# --- Create the Flask App ---
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests
logging.info("Flask app created.")

# --- Tuya Setup ---
try:
    ACCESS_ID = os.environ.get('TUYA_ACCESS_ID')
    ACCESS_KEY = os.environ.get('TUYA_ACCESS_KEY')
    DEVICE_ID = os.environ.get('TUYA_DEVICE_ID')
    API_ENDPOINT = "https://openapi.tuyaus.com"

    # Validate environment variables
    if not all([ACCESS_ID, ACCESS_KEY, DEVICE_ID]):
        logging.critical("Missing one or more required Tuya credentials in environment variables.")
        raise EnvironmentError("Missing Tuya credentials")

    openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
    openapi.connect()
    logging.info("Successfully connected to Tuya API.")

except Exception as e:
    logging.error(f"CRITICAL: Failed during Tuya setup. Error: {e}", exc_info=True)
    raise  # Exit if setup fails


# --- Constants ---
VOLTAGE_DIVISOR = 10  # Adjust this if your Tuya device reports voltage differently


# --- Define API Routes ---
@app.route('/soc')
def get_soc():
    logging.info("Request received for /soc route.")
    try:
        response = openapi.get(f"/v1.0/devices/{DEVICE_ID}/status")

        if response.get('success'):
            status_result = response['result']
            # logging.debug(f"Full status response: {status_result}")  # Uncomment for detailed debug

            # Find battery percentage DP
            battery_dp = next((item for item in status_result if item['code'] == 'BAT. Percentage'), None)

            # Find voltage DP
            voltage_dp = next((item for item in status_result if item['code'] == 'Voltage'), None)

            data_to_return = {}
            if battery_dp:
                data_to_return['soc'] = battery_dp['value']
            if voltage_dp:
                data_to_return['voltage'] = voltage_dp['value'] / VOLTAGE_DIVISOR

            if not data_to_return:
                logging.warning(f"Could not find SOC or Voltage DPs in response: {status_result}")
                return jsonify(error="Required data points not found"), 404

            logging.info(f"Successfully fetched data: {data_to_return}")
            return jsonify(data_to_return)

        else:
            logging.error(f"Tuya API call failed. Response: {response}")
            return jsonify(error="Failed to fetch data from Tuya API"), 500

    except Exception as e:
        logging.error(f"An error occurred in the get_soc function: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


@app.route('/health')
def health():
    return jsonify(status="ok")


# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
