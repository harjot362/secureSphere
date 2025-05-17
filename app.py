from flask import Flask, send_file, render_template, request, jsonify, session, redirect, url_for, flash
import mailsend, os, string, random, traceback
from supabase import create_client, Client
from flask_session import Session
from dotenv import load_dotenv
import bcrypt
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Flask setup
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Load environment variables
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Utility function to generate random strings
def gen_string(length):
    characters = string.ascii_letters + string.digits 
    return ''.join(random.choice(characters) for _ in range(length))

# Home page route
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Safe Route Finder route (example placeholder)
@app.route('/saferoute', methods=['GET'])
def safe_route():
    try:
        # TODO: Add your Safe Route Finder logic here
        return render_template('saferoute.html')
    except Exception as e:
        app.logger.error(f"Error in /saferoute: {e}")
        app.logger.error(traceback.format_exc())
        return "An error occurred loading Safe Route Finder", 500

# Clinic Finder route (example placeholder)
@app.route('/gynacfinder', methods=['GET'])
def clinic_finder():
    try:
        # TODO: Add your Clinic Finder logic here
        return render_template('gynacfinder.html')
    except Exception as e:
        app.logger.error(f"Error in /gynacfinder: {e}")
        app.logger.error(traceback.format_exc())
        return "An error occurred loading Clinic Finder", 500

# SOS page route
@app.route('/sos', methods=['GET'])
def sos_page():
    return render_template("sos.html")

# SOS alert API - fixed table name, better error handling, validation
@app.route("/sos-alert", methods=["POST"])
def sos_alert():
    data = request.get_json()
    app.logger.debug(f"Received SOS data: {data}")

    if not data:
        return jsonify({"error": "No data provided"}), 400

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    try:
        response = supabase.table("sos").insert({
            "latitude": latitude,
            "longitude": longitude,
            "description": data.get("description", ""),  # optional
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        if response.error:
            app.logger.error(f"Supabase insert error: {response.error}")
            return jsonify({"error": "Database insert failed", "details": str(response.error)}), 500

        return jsonify({"message": "SOS sent successfully"}), 200

    except Exception as e:
        app.logger.error(f"Exception during SOS alert: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": f"Failed to send SOS: {str(e)}"}), 500

# Add other routes as needed...

@app.route('/guide')
def guide():
    return render_template('guide.html')
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
