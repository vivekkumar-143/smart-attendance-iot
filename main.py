import face_recognition
import cv2
import pickle
import csv
from datetime import datetime
import time

with open("encodings.pkl", "rb") as f:
    data = pickle.load(f)

video = cv2.VideoCapture("http://192.168.1.16:8080/video")

attendance_time = {}

while True:
    ret, frame = video.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    faces = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, faces)

    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        if True in matches:
            index = matches.index(True)
            name = data["names"][index]

            if name not in attendance_time:
                attendance_time[name] = 1
            else:
                attendance_time[name] += 1

        cv2.putText(frame, name, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Smart Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()

with open("attendance.csv", "a", newline="") as f:
    writer = csv.writer(f)
    for name, minutes in attendance_time.items():
        status = "Present" if minutes >= 40 else "Absent"
        writer.writerow([name, datetime.now().date(), minutes, status])

print("Attendance Saved Successfully!")