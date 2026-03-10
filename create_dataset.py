import cv2
import os
import time

def create_dataset_from_webcam(person_name):
    dataset_path = f"dataset/authorized/{person_name}"
    os.makedirs(dataset_path, exist_ok=True)

    cap = cv2.VideoCapture(0)
    count = 0

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    print("[INFO] Starting webcam… Move your head slowly. Press 'Q' to stop.")

    last_save_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            if time.time() - last_save_time >= 0.25:
                count += 1

                # ✅ SAVE COLOR IMAGE DIRECTLY
                face_color = frame[y:y+h, x:x+w]

                cv2.imwrite(
                    f"{dataset_path}/{count}.jpg",
                    face_color
                )

                last_save_time = time.time()
                print(f"[INFO] Captured image {count}/60")

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Dataset Capture - Press Q", frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 60:
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"[INFO] Dataset completed for {person_name}! Total images: {count}")


if __name__ == "__main__":
    name = input("Enter authorized person name: ")
    create_dataset_from_webcam(name)