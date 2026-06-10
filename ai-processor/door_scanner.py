import cv2
import face_recognition
import mysql.connector
import numpy as np
import json
import requests
import time
import math
import msvcrt 
from datetime import datetime

# ==========================================
# --- CONFIGURATION ---
# ==========================================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "admin2026"
DB_NAME = "secureiot_db"

JAVA_API_URL = "http://localhost:8080/api/logs" 

# THE NEW IP ADDRESS IS HARDCODED HERE
ESP32_CMD_URL = "http://10.220.103.206"  
# ==========================================

network_state = {'is_connected': True}

def get_all_users():
    print("Fetching ALL biometric profiles from database...")
    try:
        db = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
        cursor = db.cursor()
        cursor.execute("SELECT fullname, email, face_encoding FROM users WHERE face_encoding IS NOT NULL")
        results = cursor.fetchall()
        db.close()
    except Exception as e:
        print(f"Database Error: {e}")
        return [], [], []

    known_encodings, known_names, known_emails = [], [], []
    for row in results:
        known_names.append(row[0])
        known_emails.append(row[1])
        known_encodings.append(np.array(json.loads(row[2])))
    return known_encodings, known_names, known_emails

def log_access_to_java(email, status):
    payload = {"userEmail": email, "accessStatus": status, "timestamp": datetime.now().isoformat() + "Z"}
    try: requests.post(JAVA_API_URL, json=payload, timeout=2)
    except: pass

def get_dynamic_timer():
    try:
        response = requests.get(JAVA_API_URL, timeout=2)
        if response.status_code == 200:
            logs = response.json()
            for log in reversed(logs):
                if log.get("userEmail") == "System Configuration" and str(log.get("accessStatus", "")).startswith("TIMER_"):
                    return int(log.get("accessStatus").split("_")[1])
    except Exception:
        pass
    return 5 

def trigger_hardware_unlock():
    current_timer = get_dynamic_timer()
    print(f"Signaling ESP32 Hardware: Firing Relay for {current_timer} seconds...")
    try: 
        response = requests.get(f"{ESP32_CMD_URL}/unlock?t={current_timer}", timeout=4)
        if response.status_code == 200:
            print("[SUCCESS] ESP32 confirmed the door is unlocked!")
        else:
            print(f"[WARNING] ESP32 returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e: 
        print(f"[ERROR] Failed to unlock door. Is ESP32 offline? ({e})")

def check_doorbell():
    global network_state
    try: 
        response = requests.get(f"{ESP32_CMD_URL}/button", timeout=1)
        if not network_state['is_connected']:
            print("\n[SUCCESS] Reconnected to ESP32 successfully!")
            network_state['is_connected'] = True
        return "PRESSED" in response.text.upper()
    except requests.exceptions.RequestException:
        if network_state['is_connected']:
            print(f"\n[NETWORK ERROR] Lost connection to ESP32 at {ESP32_CMD_URL}.")
            print("[INFO] Waiting for auto-recovery. You can press 'ENTER' to trigger manually.")
            network_state['is_connected'] = False
        return False

def calculate_ear(eye_points):
    A = math.dist(eye_points[1], eye_points[5])
    B = math.dist(eye_points[2], eye_points[4])
    C = math.dist(eye_points[0], eye_points[3])
    if C == 0: return 0
    return (A + B) / (2.0 * C)

def run_system():
    known_encodings, known_names, known_emails = get_all_users()
    if not known_encodings: return

    print("\n=================================================")
    print(" SYSTEM ARMED: WAITING FOR DOORBELL OR 'ENTER' ")
    print("=================================================")

    while True:
        doorbell_pressed = check_doorbell()
        
        manual_override = False
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in [b'\r', b'\n']: 
                manual_override = True
                print("\n[!] MANUAL OVERRIDE TRIGGERED VIA KEYBOARD!")
                while msvcrt.kbhit(): msvcrt.getch()

        if not doorbell_pressed and not manual_override:
            time.sleep(0.5)
            continue

        if doorbell_pressed:
            print("\n[!] PHYSICAL DOORBELL RUNG: Waking up Laptop Camera...")
            
        video_capture = cv2.VideoCapture(0)
        scan_start_time = time.time()
        SCAN_TIMEOUT = 12 
        EAR_THRESHOLD = 0.22 
        face_authorized = False
        liveness_verified = False
        consecutive_closed_frames = 0

        while time.time() - scan_start_time < SCAN_TIMEOUT:
            ret, frame = video_capture.read()
            if not ret: continue

            face_locations, face_names = [], []
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_small_frame)

            if not liveness_verified and len(face_locations) > 0:
                face_landmarks_list = face_recognition.face_landmarks(rgb_small_frame, face_locations)
                for face_landmarks in face_landmarks_list:
                    if 'left_eye' in face_landmarks and 'right_eye' in face_landmarks:
                        left_ear = calculate_ear(face_landmarks['left_eye'])
                        right_ear = calculate_ear(face_landmarks['right_eye'])
                        avg_ear = (left_ear + right_ear) / 2.0

                        if avg_ear < EAR_THRESHOLD:
                            consecutive_closed_frames += 1
                        else:
                            # ---> VIVA FIX 1: Prevent Motion Blur Fakes by requiring 3 consecutive frames <---
                            if consecutive_closed_frames >= 3:
                                liveness_verified = True
                                print("\n[LIVENESS PASSED] 3D Human Blink Detected!")
                            consecutive_closed_frames = 0

            elif liveness_verified:
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                for face_encoding in face_encodings:
                    # ---> VIVA FIX 2: Lowered tolerance from 0.60 to 0.45 for strict Zero-Trust matching <---
                    matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.45)
                    
                    name, email = "UNKNOWN", "UNKNOWN"
                    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                    
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_names[best_match_index]
                            email = known_emails[best_match_index]
                    
                    face_names.append(name)

                    if name != "UNKNOWN":
                        print(f">>> ACCESS GRANTED: Welcome, {name}! <<<")
                        trigger_hardware_unlock() 
                        log_access_to_java(email, "SUCCESS")
                        face_authorized = True
                        break 
                if face_authorized: break 

            for (top, right, bottom, left), name in zip(face_locations, face_names if liveness_verified else ["Verify Liveness"] * len(face_locations)):
                top *= 4; right *= 4; bottom *= 4; left *= 4
                color = (0, 165, 255) if not liveness_verified else ((0, 255, 0) if name != "UNKNOWN" else (0, 0, 255))
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, bottom - 10), cv2.FONT_HERSHEY_DUPLEX, 0.6, color, 1)

            if not liveness_verified:
                cv2.putText(frame, "SECURITY: PLEASE BLINK TO VERIFY LIVENESS", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            else:
                cv2.putText(frame, "LIVENESS VERIFIED. SCANNING ID...", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            time_left = int(SCAN_TIMEOUT - (time.time() - scan_start_time))
            cv2.putText(frame, f"Scanning: {time_left}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.imshow('Demo Mode Scanner', frame)
            cv2.waitKey(1)

        video_capture.release()
        cv2.destroyAllWindows()
        
        if not face_authorized:
            if not liveness_verified:
                print("Liveness Check Failed: No blink detected.")
            else:
                print("Scan timed out or face unrecognized.")
            log_access_to_java("Unknown", "DECLINED")

        print("\n=================================================")
        print(" SYSTEM ARMED: WAITING FOR DOORBELL OR 'ENTER' ")
        print("=================================================")
        time.sleep(1.5)

if __name__ == "__main__":
    run_system()