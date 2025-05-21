# from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
# import os, string, random, traceback, threading, logging
# from supabase import create_client, Client
# from flask_session import Session
# from dotenv import load_dotenv
# from datetime import datetime
# import cv2
# import numpy as np
# import pygame
# import bcrypt
# import face_recognition
# from flask_cors import CORS
# import smtplib 
# from email.mime.text import MIMEText

# app = Flask(__name__)
# CORS(app, supports_credentials=True)


# # Load environment variables from .env file
# load_dotenv()

# # ============ Logging ============
# logging.basicConfig(level=logging.DEBUG)

# # ============ Flask Setup ============
# app = Flask(__name__)
# app.secret_key = os.urandom(24)
# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)

# pygame.mixer.init()

# # ============ Supabase ============
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# # ============ Helpers ============
# def gen_string(length):
#     characters = string.ascii_letters + string.digits 
#     return ''.join(random.choice(characters) for _ in range(length))

# forum_posts = []

# # ============ Edit Profile ============
# @app.route("/editprofile", methods=["GET", "POST"])
# def edit_profile():
#     if "user" not in session:
#         return redirect(url_for("login"))

#     user_email = session["user"]["email"]

#     if request.method == "POST":
#         name = request.form["name"]
#         age = request.form["age"]
#         phone = request.form["phone"]
#         blood = request.form["blood"]
#         email = request.form["email"]
#         emergency_con = request.form["emergency_con"]
#         password = request.form["password"]
#         cpassword = request.form["cpassword"]

#         if password != cpassword:
#             return "Passwords do not match", 400

#         supabase.table("users").update({
#             "name": name,
#             "age": age,
#             "phone": phone,
#             "blood_group": blood,
#             "email": email,
#             "emergency_con": emergency_con,
#             "password": password
#         }).eq("email", user_email).execute()

#         session["user"].update({
#             "name": name,
#             "age": age,
#             "phone": phone,
#             "blood_group": blood,
#             "email": email,
#             "emergency_con": emergency_con,
#             "password": password
#         })

#         return redirect(url_for("edit_profile"))

#     response = supabase.table("users").select("*").eq("email", user_email).single().execute()
#     user = response.data

#     return render_template("editprofile.html", user=user)

# # ============ Login ============
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]

#         response = supabase.table("users").select("*").eq("email", email).single().execute()

#         if response.data:
#             user = response.data
#             if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
#                 session["user"] = user
#                 return redirect(url_for("home"))

#         return "Invalid credentials", 400

#     return render_template("login.html")

# # ============ Paths ============
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# CASCADE_PATH = os.path.join(BASE_DIR, 'static', 'shieldcam', 'haarcascade_frontalface_default.xml')
# ALARM_PATH = os.path.join(BASE_DIR, 'static', 'shieldcam', 'alarm.mp3')

# if not os.path.exists(CASCADE_PATH):
#     raise FileNotFoundError(f"Haarcascade not found at {CASCADE_PATH}")
# face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# alarm_triggered = False

# def play_alarm():
#     global alarm_triggered
#     if alarm_triggered:
#         return
#     alarm_triggered = True

#     def _play():
#         try:
#             pygame.mixer.music.load(ALARM_PATH)
#             pygame.mixer.music.play()
#             while pygame.mixer.music.get_busy():
#                 pygame.time.Clock().tick(10)
#         except Exception as e:
#             app.logger.error(f"Error playing alarm: {e}")
#         finally:
#             global alarm_triggered
#             alarm_triggered = False

#     threading.Thread(target=_play, daemon=True).start()

# # ============ Load Known Faces ============
# known_face_encodings = []
# known_face_names = []

# KNOWN_FACES_DIR = os.path.join(BASE_DIR, "flask_session", "known_faces")
# if not os.path.exists(KNOWN_FACES_DIR):
#     os.makedirs(KNOWN_FACES_DIR)

# for filename in os.listdir(KNOWN_FACES_DIR):
#     if filename.lower().endswith((".jpg", ".png")):
#         path = os.path.join(KNOWN_FACES_DIR, filename)
#         image = face_recognition.load_image_file(path)
#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             known_face_encodings.append(encodings[0])
#             known_face_names.append(os.path.splitext(filename)[0])

# # ============ ShieldCam ============
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

#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Unknown"

#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
#             cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

#             if name == "Unknown":
#                 play_alarm()

#                 timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#                 face_image = frame[top:bottom, left:right]
#                 unknown_dir = os.path.join(BASE_DIR, 'flask_session', 'ShieldCam', 'detected_faces')
#                 os.makedirs(unknown_dir, exist_ok=True)
#                 save_path = os.path.join(unknown_dir, f"unknown_{timestamp}.jpg")
#                 cv2.imwrite(save_path, face_image)

#         ret, buffer = cv2.imencode('.jpg', frame)
#         if not ret:
#             break

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

#     camera.release()

# # ============ Routes ============
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

# # Email config — replace with your real credentials
# EMAIL_ADDRESS = "harjotkb2004@gmail.com"
# EMAIL_PASSWORD = "qhhytzdosqpqnhhk"  # Use Gmail App Password if 2FA enabled
# RECEIVER_EMAIL = "harjot362.be22@chitkara.edu.in"
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587


# @app.route('/sos-alert', methods=['POST'])
# def sos_alert():
#     data = request.get_json()
#     latitude = data.get('latitude')
#     longitude = data.get('longitude')
#     print(f"Received SOS location: lat={latitude}, long={longitude}")
#     # Here you could save to DB or do something else
#     return jsonify({"message": "SOS location received"}), 200


# @app.route('/send-sos-email', methods=['POST'])
# def send_sos_email():
#     try:
#         data = request.get_json()
#         message = data.get('message')

#         if not message:
#             return jsonify({"message": "No message provided"}), 400

#         msg = MIMEText(message)
#         msg['Subject'] = "Emergency SOS Alert"
#         msg['From'] = EMAIL_ADDRESS
#         msg['To'] = RECEIVER_EMAIL

#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.starttls()
#         server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#         server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg.as_string())
#         server.quit()

#         print("Email sent successfully!")
#         return jsonify({"message": "SOS email sent successfully"}), 200

#     except Exception as e:
#         print(f"Failed to send email: {e}")  # <-- Print detailed error
#         return jsonify({"message": f"Failed to send email: {str(e)}"}), 500


# if __name__ == '__main__':
#     app.run(debug=True)

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

# @app.route('/shieldCam')
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

# # ============ Run App ============
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)


from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
import os
import string
import random
import threading
import logging
from supabase import create_client, Client
from flask_session import Session
from dotenv import load_dotenv
from datetime import datetime
import cv2
import numpy as np
import pygame
import bcrypt
import face_recognition
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText

# ============ Flask Setup ============
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Load environment variables from .env file
load_dotenv()

app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# ============ Logging ============
logging.basicConfig(level=logging.DEBUG)

# Initialize pygame mixer for alarm sound
pygame.mixer.init()

# ============ Supabase ============
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============ Helpers ============
def gen_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

forum_posts = []

# ============ Paths ============
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CASCADE_PATH = os.path.join(BASE_DIR, 'static', 'shieldcam', 'haarcascade_frontalface_default.xml')
ALARM_PATH = os.path.join(BASE_DIR, 'static', 'shieldcam', 'alarm.mp3')

if not os.path.exists(CASCADE_PATH):
    raise FileNotFoundError(f"Haarcascade not found at {CASCADE_PATH}")

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# ============ Alarm Handling ============
alarm_triggered = False
alarm_lock = threading.Lock()

def play_alarm():
    global alarm_triggered
    with alarm_lock:
        if alarm_triggered:
            return
        alarm_triggered = True

    def _play():
        try:
            pygame.mixer.music.load(ALARM_PATH)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            app.logger.error(f"Error playing alarm: {e}")
        finally:
            global alarm_triggered
            with alarm_lock:
                alarm_triggered = False

    threading.Thread(target=_play, daemon=True).start()

# ============ Load Known Faces ============
known_face_encodings = []
known_face_names = []

KNOWN_FACES_DIR = os.path.join(BASE_DIR, "flask_session", "known_faces")
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.lower().endswith((".jpg", ".png")):
        path = os.path.join(KNOWN_FACES_DIR, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(filename)[0])

# ============ ShieldCam Video Feed ============
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

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if name == "Unknown":
                play_alarm()

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                face_image = frame[top:bottom, left:right]
                unknown_dir = os.path.join(BASE_DIR, 'flask_session', 'ShieldCam', 'detected_faces')
                os.makedirs(unknown_dir, exist_ok=True)
                save_path = os.path.join(unknown_dir, f"unknown_{timestamp}.jpg")
                cv2.imwrite(save_path, face_image)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
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

# Email config — replace with your real credentials
EMAIL_ADDRESS = "harjotkb2004@gmail.com"
EMAIL_PASSWORD = "aumuvdjlwryyqtxc"  # Use Gmail App Password if 2FA enabled
RECEIVER_EMAIL = "harjot362.be22@chitkara.edu.in"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

@app.route('/sos-alert', methods=['POST'])
def sos_alert():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    app.logger.info(f"Received SOS location: lat={latitude}, long={longitude}")
    # Save or process the location as needed
    return jsonify({"message": "SOS location received"}), 200

@app.route('/send-sos-email', methods=['POST'])
def send_sos_email():
    try:
        data = request.get_json()
        message = data.get('message')

        if not message:
            return jsonify({"message": "No message provided"}), 400

        msg = MIMEText(message)
        msg['Subject'] = "Emergency SOS Alert"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECEIVER_EMAIL

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg.as_string())
        server.quit()

        app.logger.info("SOS email sent successfully!")
        return jsonify({"message": "SOS email sent successfully"}), 200

    except Exception as e:
        app.logger.error(f"Failed to send email: {e}")
        return jsonify({"message": f"Failed to send email: {str(e)}"}), 500

# ============ User Authentication ============

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        response = supabase.table("users").select("*").eq("email", email).single().execute()

        if response.data:
            user = response.data
            stored_hash = user.get("password")
            if stored_hash and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                session["user"] = user
                return redirect(url_for("home"))

        return "Invalid credentials", 400

    return render_template("login.html")

@app.route("/editprofile", methods=["GET", "POST"])
def edit_profile():
    if "user" not in session:
        return redirect(url_for("login"))

    user_email = session["user"]["email"]

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        phone = request.form["phone"]
        blood = request.form["blood"]
        email = request.form["email"]
        emergency_con = request.form["emergency_con"]
        password = request.form["password"]
        cpassword = request.form["cpassword"]

        if password != cpassword:
            return "Passwords do not match", 400

        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        supabase.table("users").update({
            "name": name,
            "age": age,
            "phone": phone,
            "blood_group": blood,
            "email": email,
            "emergency_con": emergency_con,
            "password": hashed_password
        }).eq("email", user_email).execute()

        # Update session data with new values
        session["user"].update({
            "name": name,
            "age": age,
            "phone": phone,
            "blood_group": blood,
            "email": email,
            "emergency_con": emergency_con,
            "password": hashed_password
        })

        return redirect(url_for("edit_profile"))

    response = supabase.table("users").select("*").eq("email", user_email).single().execute()
    user = response.data

    return render_template("editprofile.html", user=user)

# ============ Forum ============
@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if request.method == 'POST':
        username = request.form.get('username')
        message = request.form.get('post')
        if username and message:
            forum_posts.append({'username': username, 'message': message})
        return redirect('/forum')
    return render_template('forum.html', posts=forum_posts)

# ============ ShieldCam ============
@app.route('/shieldCam')
def shieldcam():
    return render_template('shieldCam.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ============ Other Pages ============
@app.route('/guide_cards')
def guide():
    return render_template('guide_cards.html')

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
