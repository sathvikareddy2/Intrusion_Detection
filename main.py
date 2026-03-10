import cv2
import numpy as np
import pickle
import os
import time
import datetime
from deepface import DeepFace
import smtplib
from email.message import EmailMessage
from playsound import playsound
import threading

# =========================
# CONFIGURATION
# =========================
EMB_FILE = "trainer/embeddings.pickle"
LOG_DIR = "logs/intruder_images"
LOG_FILE = "logs/log.csv"

THRESHOLD = 0.60
COOLDOWN = 10

# =========================
# EMAIL CONFIGURATION
# =========================
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
EMAIL_RECEIVER = "receiver_email@gmail.com"

# =========================
# SETUP
# =========================
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("timestamp,name,filename\n")

# Load embeddings
data = pickle.load(open(EMB_FILE, "rb"))
known_names = list(data.keys())
known_embeddings = np.array(list(data.values()))

print("[INFO] Face embeddings loaded successfully.")

# Haar cascade
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

last_alert_time = 0
frame_count = 0

# =========================
# COSINE SIMILARITY
# =========================
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# =========================
# ALARM FUNCTION
# =========================
def play_alarm():
    try:
        playsound("alarm.wav")
    except:
        print("Alarm sound error")

# =========================
# EMAIL ALERT FUNCTION
# =========================
def send_email_alert(image_path):

    try:
        msg = EmailMessage()
        msg["Subject"] = "🚨 Intruder Alert Detected!"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        msg.set_content("Intruder detected by AI Surveillance System.")

        with open(image_path, "rb") as f:
            img_data = f.read()
            img_name = os.path.basename(image_path)

        msg.add_attachment(
            img_data,
            maintype="image",
            subtype="jpeg",
            filename=img_name
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print("[INFO] Email alert sent.")

    except Exception as e:
        print("Email error:", e)

# =========================
# LOG INTRUDER
# =========================
def log_intruder(face_img):

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"intruder_{timestamp}.jpg"
    filepath = os.path.join(LOG_DIR, filename)

    cv2.imwrite(filepath, face_img)

    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp},INTRUDER,{filename}\n")

    print(f"[ALERT] Intruder logged at {timestamp}")

    # Send email alert
    threading.Thread(target=send_email_alert, args=(filepath,)).start()

# =========================
# START CAMERA
# =========================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("[INFO] Surveillance started — press Q to exit")

while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if frame_count % 2 == 0:

        for (x, y, w, h) in faces:

            face_img = frame[y:y+h, x:x+w]

            if face_img.shape[0] < 50 or face_img.shape[1] < 50:
                continue

            try:

                result = DeepFace.represent(
                    img_path=face_img,
                    model_name="Facenet",
                    enforce_detection=False
                )

                embedding = np.array(result[0]["embedding"])

                similarities = [
                    cosine_similarity(embedding, known_emb)
                    for known_emb in known_embeddings
                ]

                max_sim = max(similarities)
                best_match_idx = similarities.index(max_sim)

                if max_sim > THRESHOLD:

                    name = known_names[best_match_idx]
                    color = (0, 255, 0)

                else:

                    name = "INTRUDER"
                    color = (0, 0, 255)

                    current_time = time.time()

                    if current_time - last_alert_time > COOLDOWN:

                        # Save intruder
                        log_intruder(face_img)

                        # Play alarm
                        threading.Thread(target=play_alarm).start()

                        last_alert_time = current_time

            except Exception as e:

                print("ERROR:", e)
                name = "Error"
                color = (0, 255, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

            cv2.putText(
                frame,
                name,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

    cv2.imshow("AI Intrusion Detection", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('Q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()

print("[INFO] Surveillance stopped")