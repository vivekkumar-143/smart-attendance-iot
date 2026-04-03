import face_recognition
import os
import pickle

known_encodings = []
known_names = []

dataset_path = "dataset"

for filename in os.listdir(dataset_path):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(dataset_path, filename)
        image = face_recognition.load_image_file(image_path)
        
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(filename.split(".")[0])

data = {"encodings": known_encodings, "names": known_names}

with open("encodings.pkl", "wb") as f:
    pickle.dump(data, f)

print("Enrollment Completed Successfully!")