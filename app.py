
# from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
# import mailsend, os, string, random, traceback
# from supabase import create_client, Client
# from flask_session import Session
# from dotenv import load_dotenv
# import bcrypt
# from datetime import datetime
# import logging
# import cv2
# import face_recognition
# import numpy as np
# from playsound import playsound
# import threading

# # Setup logging
# logging.basicConfig(level=logging.DEBUG)

# # Flask setup
# app = Flask(__name__)
# app.secret_key = os.urandom(24)
# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)

# # Load environment variables
# load_dotenv()

# # Supabase setup
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# # Utility function to generate random strings
# def gen_string(length):
#     characters = string.ascii_letters + string.digits 
#     return ''.join(random.choice(characters) for _ in range(length))

# # Global forum posts
# forum_posts = []

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/saferoute')
# def safe_route():
#     return render_template('saferoute.html')

# @app.route('/gynacfinder')
# def clinic_finder():
#     return render_template('gynacfinder.html')

# @app.route('/sos')
# def sos_page():
#     return render_template("sos.html")

# @app.route("/sos-alert", methods=["POST"])
# def sos_alert():
#     data = request.get_json()
#     app.logger.debug(f"Received SOS data: {data}")
#     if not data:
#         return jsonify({"error": "No data provided"}), 400

#     latitude = data.get("latitude")
#     longitude = data.get("longitude")

#     if latitude is None or longitude is None:
#         return jsonify({"error": "Latitude and longitude are required"}), 400

#     try:
#         response = supabase.table("sos").insert({
#             "latitude": latitude,
#             "longitude": longitude,
#             "description": data.get("description", ""),
#             "created_at": datetime.utcnow().isoformat()
#         }).execute()

#         if response.error:
#             return jsonify({"error": "Database insert failed", "details": str(response.error)}), 500

#         return jsonify({"message": "SOS sent successfully"}), 200

#     except Exception as e:
#         app.logger.error(traceback.format_exc())
#         return jsonify({"error": f"Failed to send SOS: {str(e)}"}), 500

# @app.route('/guide_cards')
# def guide():
#     return render_template('guide_cards.html')

# @app.route('/forum', methods=['GET', 'POST'])
# def forum():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         message = request.form.get('post')
#         if username and message:
#             forum_posts.append({'username': username, 'message': message})
#         return redirect('/forum')
#     return render_template('forum.html', posts=forum_posts)

# # === ShieldCam ===

# # Paths
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# CASCADE_PATH = os.path.join(BASE_DIR, 'static', 'shieldcam', 'haarcascade_frontalface_default.xml')
# ALARM_PATH = os.path.join(BASE_DIR, 'static', 'shieldcam', 'alarm.mp3')

# # Load Haar Cascade
# if not os.path.exists(CASCADE_PATH):
#     raise FileNotFoundError(f"Haarcascade file not found at {CASCADE_PATH}")
# face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# # Placeholder for known faces
# known_face_encodings = []
# known_face_names = []

# def play_alarm():
#     if os.path.exists(ALARM_PATH):
#         threading.Thread(target=playsound, args=(ALARM_PATH,), daemon=True).start()
#     else:
#         app.logger.warning("Alarm file not found!")

# def gen_frames():
#     camera = cv2.VideoCapture(0)
#     if not camera.isOpened():
#         app.logger.error("Could not open webcam")
#         return

#     while True:
#         success, frame = camera.read()
#         if not success:
#             app.logger.error("Failed to read frame")
#             break

#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

#         for (x, y, w, h) in faces:
#             cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
#             play_alarm()

#         ret, buffer = cv2.imencode('.jpg', frame)
#         if not ret:
#             app.logger.error("Failed to encode frame")
#             break
#         frame_bytes = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

#     camera.release()

# @app.route('/shieldcam')
# def shieldcam():
#     return render_template('shieldCam.html')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route("/routes")
# def list_routes():
#     import urllib
#     output = []
#     for rule in app.url_map.iter_rules():
#         methods = ','.join(rule.methods)
#         line = urllib.parse.unquote(f"{rule.endpoint:30s} {methods:20s} {str(rule)}")
#         output.append(line)
#     return "<pre>" + "\n".join(output) + "</pre>"


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)




from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
import os, string, random, traceback, threading, logging
from supabase import create_client, Client
from flask_session import Session
from dotenv import load_dotenv
from datetime import datetime
import cv2
import numpy as np
import pygame

# Load environment variables from .env file
load_dotenv()

# ============ Setup Logging ============
logging.basicConfig(level=logging.DEBUG)

# ============ Flask App Setup ============
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Initialize pygame mixer for alarm sound
pygame.mixer.init()

# ============ Load Environment Variables ============
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ============ Supabase Client ============
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============ Helper Functions ============
def gen_string(length):
    characters = string.ascii_letters + string.digits 
    return ''.join(random.choice(characters) for _ in range(length))

# ============ Forum Data ============
forum_posts = []

# ============ Static Paths ============
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CASCADE_PATH = os.path.join(BASE_DIR, 'static', 'shieldcam', 'haarcascade_frontalface_default.xml')
ALARM_PATH = os.path.join(BASE_DIR, 'static', 'shieldcam', 'alarm.mp3')

# ============ Haar Cascade ============
if not os.path.exists(CASCADE_PATH):
    raise FileNotFoundError(f"Haarcascade not found at {CASCADE_PATH}")
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# ============ Alarm Trigger ============
alarm_triggered = False

def play_alarm():
    global alarm_triggered
    if alarm_triggered:
        return
    alarm_triggered = True

    def _play():
        try:
            pygame.mixer.music.load(ALARM_PATH)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # wait for sound to finish
        except Exception as e:
            app.logger.error(f"Error playing alarm: {e}")
        finally:
            global alarm_triggered
            alarm_triggered = False

    threading.Thread(target=_play, daemon=True).start()

# ============ Video Feed Generator ============
def gen_frames():
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        app.logger.error("Could not open webcam")
        return

    while True:
        success, frame = camera.read()
        if not success:
            app.logger.error("Failed to read frame")
            break

        # Face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            play_alarm()

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            app.logger.error("Frame encoding failed")
            break

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    camera.release()

# ============ Routes ============

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/saferoute')
def safe_route():
    return render_template('saferoute.html')

@app.route('/gynacfinder')
def clinic_finder():
    return render_template('gynacfinder.html')

@app.route('/sos')
def sos_page():
    return render_template("sos.html")

@app.route("/sos-alert", methods=["POST"])
def sos_alert():
    data = request.get_json()
    app.logger.debug(f"Received SOS data: {data}")

    if not data:
        return jsonify({"error": "No data provided"}), 400

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    description = data.get("description", "")

    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and longitude required"}), 400

    try:
        response = supabase.table("sos").insert({
            "latitude": latitude,
            "longitude": longitude,
            "description": description,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        if response.error:
            app.logger.error(f"Supabase insert error: {response.error}")
            return jsonify({"error": "Database error", "details": str(response.error)}), 500

        return jsonify({"message": "SOS sent successfully"}), 200

    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({"error": f"Exception: {str(e)}"}), 500

@app.route('/guide_cards')
def guide():
    return render_template('guide_cards.html')

@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if request.method == 'POST':
        username = request.form.get('username')
        message = request.form.get('post')
        if username and message:
            forum_posts.append({'username': username, 'message': message})
        return redirect('/forum')
    return render_template('forum.html', posts=forum_posts)

@app.route('/shieldcam')
def shieldcam():
    return render_template('shieldCam.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/routes")
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint:30s} {methods:20s} {str(rule)}")
        output.append(line)
    return "<pre>" + "\n".join(output) + "</pre>"

# ============ Run App ============
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
