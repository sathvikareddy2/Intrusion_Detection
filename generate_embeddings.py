import os
import pickle
import numpy as np
from deepface import DeepFace

DATASET_DIR = "dataset/authorized"
EMBEDDINGS_PATH = "trainer/embeddings.pickle"

def generate_embeddings():
    person_embeddings = {}

    for person_name in os.listdir(DATASET_DIR):
        person_folder = os.path.join(DATASET_DIR, person_name)

        if not os.path.isdir(person_folder):
            continue

        embeddings_list = []

        for img_name in os.listdir(person_folder):
            if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            img_path = os.path.join(person_folder, img_name)

            try:
                result = DeepFace.represent(
                    img_path=img_path,
                    model_name="Facenet",
                    enforce_detection=False
                )

                embedding = result[0]["embedding"]
                embeddings_list.append(embedding)

                print(f"[INFO] Processed {img_path}")

            except Exception:
                print(f"[WARNING] Skipped {img_path}")

        if len(embeddings_list) > 0:
            mean_embedding = np.mean(embeddings_list, axis=0)
            person_embeddings[person_name] = mean_embedding

    os.makedirs("trainer", exist_ok=True)

    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(person_embeddings, f)

    print("[SUCCESS] Embeddings generated successfully!")

if __name__ == "__main__":
    generate_embeddings()