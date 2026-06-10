from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import face_recognition
import mysql.connector
import numpy as np
import json
import base64
from datetime import datetime

app = Flask(__name__)
# Allow the HTML Dashboard to talk to this Python API
CORS(app) 

# --- CONFIGURATION ---
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "admin2026"
DB_NAME = "secureiot_db"

@app.route('/register', methods=['POST'])
def register_face():
    data = request.json
    email = data.get('email')
    image_data = data.get('image')
    force_overwrite = data.get('force_overwrite', False)

    if not email or not image_data:
        return jsonify({"error": "Missing email or image data"}), 400

    try:
        db = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
        cursor = db.cursor()
        
        # 1. Verify user exists and check if they already have a face registered
        cursor.execute("SELECT fullname, face_encoding FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": f"No user found with email '{email}'. Please create the user first."}), 404

        fullname = result[0]
        existing_encoding = result[1]

        # 2. OVERWRITE PROTECTION: If face exists and admin hasn't confirmed yet, ask them!
        if existing_encoding is not None and not force_overwrite:
            return jsonify({
                "require_confirmation": True,
                "message": f"{fullname} already has a registered face profile. Do you want to overwrite it with this new capture?"
            }), 200

        # 3. Decode the image sent from the web browser
        header, encoded = image_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        img_arr = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_arr, flags=cv2.IMREAD_COLOR)
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # 4. Process the Face Biometrics
        face_encodings = face_recognition.face_encodings(rgb_frame)
        
        # Strict validation checks
        if len(face_encodings) == 0:
            return jsonify({"error": "No face detected! Please ensure good lighting and look directly at the camera."}), 400
        if len(face_encodings) > 1:
            return jsonify({"error": "Multiple faces detected! Please ensure only one person is in the frame."}), 400

        encoding_json = json.dumps(face_encodings[0].tolist())
        
        # Get exact registration time
        registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 5. Save to MySQL
        # (Note: If your database has a specific column for time like 'date_registered', you can add it to this SQL statement!)
        cursor.execute("UPDATE users SET face_encoding = %s WHERE email = %s", (encoding_json, email))
        db.commit()

        print(f"[{registration_time}] Successfully registered/updated face for: {fullname}")
        return jsonify({"success": True, "message": f"Success! Face registered for {fullname}."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'db' in locals() and db.is_connected():
            db.close()

if __name__ == '__main__':
    print("=== SECURE IOT: FACE REGISTRATION API ONLINE ===")
    print("Running on http://localhost:5000")
    print("Waiting for web dashboard requests...")
    app.run(port=5000)