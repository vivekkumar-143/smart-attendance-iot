# # import cv2
# # import numpy as np
# # import face_recognition
# # import os
# # import pandas as pd
# # from datetime import datetime
# # import pyttsx3
# # import threading
# # from queue import Queue
# # import time
# # import winsound
# # import serial

# # # ==============================  
# # # IoT: ESP32 Serial Setup
# # arduino = serial.Serial('COM5', 9600)  # Apna ESP32 COM port
# # time.sleep(2)  # connection stabilize

# # def set_led_buzzer(green, red, buzzer):
# #     """
# #     green, red, buzzer = 0 or 1
# #     Send string to Arduino in format "G,R,B\n"
# #     """
# #     cmd = f"{green},{red},{buzzer}\n"
# #     arduino.write(cmd.encode())

# # # ==============================  
# # # NON-BLOCKING VOICE SYSTEM
# # engine = pyttsx3.init()
# # engine.setProperty('rate', 150)
# # voice_queue = Queue()

# # def voice_worker():
# #     while True:
# #         text = voice_queue.get()
# #         if text is None:
# #             break
# #         engine.say(text)
# #         engine.runAndWait()
# #         voice_queue.task_done()

# # threading.Thread(target=voice_worker, daemon=True).start()
# # def speak(text):
# #     voice_queue.put(text)

# # # ==============================  
# # # SETTINGS
# # PERIOD_DURATION = 50 * 60
# # STRICT_THRESHOLD = 0.65
# # FRAME_SKIP = 3
# # EXIT_DELAY = 3
# # MIN_REQUIRED_TIME = 40 * 60  # 40 minutes for PRESENT

# # # ==============================  
# # # LOAD DATASET
# # path = "dataset"
# # images = []
# # classNames = []

# # for student_name in os.listdir(path):
# #     student_folder = os.path.join(path, student_name)
# #     if os.path.isdir(student_folder):
# #         img_files = os.listdir(student_folder)
# #         if len(img_files) == 0:
# #             continue
# #         img_path = os.path.join(student_folder, img_files[0])
# #         img = cv2.imread(img_path)
# #         if img is not None:
# #             images.append(img)
# #             classNames.append(student_name)

# # print("Students Loaded:", classNames)

# # # ==============================  
# # # ENCODE FACES
# # def findEncodings(images, classNames):
# #     encodeList = []
# #     validClassNames = []

# #     for img, name in zip(images, classNames):
# #         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# #         encodes = face_recognition.face_encodings(img)

# #         if len(encodes) > 0:
# #             encodeList.append(encodes[0])
# #             validClassNames.append(name)
# #         else:
# #             print(f"Encoding failed for {name}")

# #     return encodeList, validClassNames

# # known_encodings, classNames = findEncodings(images, classNames)
# # print("Encoding Completed")

# # # ==============================  
# # attendance_data = {}
# # last_seen = {}

# # def mark_attendance(name, now, action):
# #     if name not in attendance_data:
# #         attendance_data[name] = {
# #             "last_entry": None,
# #             "total_time": 0,
# #             "status": "OUT",
# #             "date": now.strftime("%d-%m-%Y"),
# #             "day": now.strftime("%A"),
# #             "entry_time": None,
# #             "exit_time": None
# #         }

# #     student = attendance_data[name]

# #     if action == "IN":
# #         student["last_entry"] = now
# #         student["status"] = "IN"
# #         if student["entry_time"] is None:
# #             student["entry_time"] = now.strftime("%H:%M:%S")

# #     elif action == "OUT" and student["status"] == "IN":
# #         duration = (now - student["last_entry"]).total_seconds()
# #         student["total_time"] += duration
# #         student["status"] = "OUT"
# #         student["exit_time"] = now.strftime("%H:%M:%S")

# # # ==============================  
# # cap = cv2.VideoCapture(0)
# # print("Camera Started... Press Q to Stop")

# # frame_count = 0
# # start_time = datetime.now()
# # OUTSIDER_COOLDOWN = 5
# # last_outsider_time = 0

# # while True:
# #     success, img = cap.read()
# #     if not success:
# #         continue

# #     frame_count += 1
# #     if frame_count % FRAME_SKIP != 0:
# #         continue

# #     imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
# #     imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

# #     facesCurFrame = face_recognition.face_locations(imgSmall)
# #     encodesCurFrame = face_recognition.face_encodings(imgSmall, facesCurFrame)

# #     now = datetime.now()
# #     current_time = time.time()
# #     detected_names = []

# #     for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
# #         face_distances = face_recognition.face_distance(known_encodings, encodeFace)
# #         if len(face_distances) != 0:
# #             best_match_index = np.argmin(face_distances)
# #             if face_distances[best_match_index] < STRICT_THRESHOLD:
# #                 name = classNames[best_match_index].upper()
# #             else:
# #                 name = "OUTSIDER"
# #         else:
# #             name = "OUTSIDER"

# #         y1, x2, y2, x1 = faceLoc
# #         y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
# #         color = (0,255,0) if name!="OUTSIDER" else (0,0,255)
# #         cv2.rectangle(img,(x1,y1),(x2,y2),color,2)
# #         cv2.putText(img,name,(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,color,2)

# #         # ===== OUTSIDER =====
# #         if name == "OUTSIDER":
# #             set_led_buzzer(green=0, red=1, buzzer=1)  # Red + Buzzer ON, Green OFF
# #             if current_time - last_outsider_time > OUTSIDER_COOLDOWN:
# #                 winsound.Beep(1500, 800)
# #                 speak("Alert! Outsider detected")
# #                 last_outsider_time = current_time
# #             continue

# #         # ===== KNOWN STUDENT =====
# #         detected_names.append(name)
# #         set_led_buzzer(green=1, red=0, buzzer=0)  # Green ON, Red & Buzzer OFF

# #         if name not in attendance_data or attendance_data[name]["status"] == "OUT":
# #             speak(f"{name} Enter")
# #             mark_attendance(name, now, "IN")

# #         last_seen[name] = current_time

# #     # ===== EXIT CHECK =====
# #     for name in list(attendance_data.keys()):
# #         if attendance_data[name]["status"] == "IN":
# #             if name not in detected_names:
# #                 time_gap = current_time - last_seen.get(name, 0)
# #                 if time_gap > EXIT_DELAY:
# #                     speak(f"{name} Exit")
# #                     mark_attendance(name, now, "OUT")
# #                     if name in last_seen:
# #                         del last_seen[name]

# #     cv2.imshow("Smart Attendance System", img)

# #     if (now - start_time).total_seconds() > PERIOD_DURATION:
# #         break

# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # # ==============================  
# # # FINAL ATTENDANCE WITH PRESENT / ABSENT
# # final_data = []

# # for name, data in attendance_data.items():
# #     if data["status"] == "IN":
# #         duration = (datetime.now() - data["last_entry"]).total_seconds()
# #         data["total_time"] += duration

# #     total_minutes = round(data["total_time"] / 60, 2)
# #     attendance_status = "PRESENT" if data["total_time"] >= MIN_REQUIRED_TIME else "ABSENT"

# #     final_data.append({
# #         "Name": name,
# #         "Date": data["date"],
# #         "Day": data["day"],
# #         "Entry_Time": data["entry_time"],
# #         "Exit_Time": data["exit_time"],
# #         "Total_Minutes": total_minutes,
# #         "Attendance_Status": attendance_status
# #     })

# # df = pd.DataFrame(final_data)
# # df.to_csv("attendance.csv", index=False)

# # cap.release()
# # cv2.destroyAllWindows()

# # print("Attendance saved successfully with Present/Absent status!")
# # set_led_buzzer(green=0, red=0, buzzer=0)  # Turn off all at end



# # import cv2
# # import numpy as np
# # import face_recognition
# # import os
# # import pandas as pd
# # from datetime import datetime
# # import pyttsx3
# # import threading
# # from queue import Queue
# # import time
# # import winsound
# # import serial

# # # ==============================  
# # # IoT: ESP32 Serial Setup
# # arduino = serial.Serial('COM5', 9600)  # Apna ESP32 COM port
# # time.sleep(2)  # connection stabilize

# # def set_led_buzzer(green, red, buzzer):
# #     """
# #     green, red, buzzer = 0 or 1
# #     Send string to Arduino in format "G,R,B\n"
# #     """
# #     cmd = f"{green},{red},{buzzer}\n"
# #     arduino.write(cmd.encode())

# # # ==============================  
# # # NON-BLOCKING VOICE SYSTEM
# # engine = pyttsx3.init()
# # engine.setProperty('rate', 150)
# # voice_queue = Queue()

# # def voice_worker():
# #     while True:
# #         text = voice_queue.get()
# #         if text is None:
# #             break
# #         engine.say(text)
# #         engine.runAndWait()
# #         voice_queue.task_done()

# # threading.Thread(target=voice_worker, daemon=True).start()
# # def speak(text):
# #     voice_queue.put(text)

# # # ==============================  
# # # SETTINGS
# # PERIOD_DURATION = 50 * 60
# # STRICT_THRESHOLD = 0.65
# # FRAME_SKIP = 3
# # EXIT_DELAY = 3
# # MIN_REQUIRED_TIME = 40 * 60  # 40 minutes for PRESENT

# # # ==============================  
# # # LOAD DATASET
# # path = "dataset"
# # images = []
# # classNames = []

# # for student_name in os.listdir(path):
# #     student_folder = os.path.join(path, student_name)
# #     if os.path.isdir(student_folder):
# #         img_files = os.listdir(student_folder)
# #         if len(img_files) == 0:
# #             continue
# #         img_path = os.path.join(student_folder, img_files[0])
# #         img = cv2.imread(img_path)
# #         if img is not None:
# #             images.append(img)
# #             classNames.append(student_name)

# # print("Students Loaded:", classNames)

# # # ==============================  
# # # ENCODE FACES
# # def findEncodings(images, classNames):
# #     encodeList = []
# #     validClassNames = []

# #     for img, name in zip(images, classNames):
# #         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# #         encodes = face_recognition.face_encodings(img)

# #         if len(encodes) > 0:
# #             encodeList.append(encodes[0])
# #             validClassNames.append(name)
# #         else:
# #             print(f"Encoding failed for {name}")

# #     return encodeList, validClassNames

# # known_encodings, classNames = findEncodings(images, classNames)
# # print("Encoding Completed")

# # # ==============================  
# # attendance_data = {}
# # last_seen = {}

# # def mark_attendance(name, now, action):
# #     if name not in attendance_data:
# #         attendance_data[name] = {
# #             "last_entry": None,
# #             "total_time": 0,
# #             "status": "OUT",
# #             "date": now.strftime("%d-%m-%Y"),
# #             "day": now.strftime("%A"),
# #             "entry_time": None,
# #             "exit_time": None
# #         }

# #     student = attendance_data[name]

# #     if action == "IN":
# #         student["last_entry"] = now
# #         student["status"] = "IN"
# #         if student["entry_time"] is None:
# #             student["entry_time"] = now.strftime("%H:%M:%S")

# #     elif action == "OUT" and student["status"] == "IN":
# #         duration = (now - student["last_entry"]).total_seconds()
# #         student["total_time"] += duration
# #         student["status"] = "OUT"
# #         student["exit_time"] = now.strftime("%H:%M:%S")

# # # ==============================  
# # cap = cv2.VideoCapture(0)
# # print("Camera Started... Press Q to Stop")

# # frame_count = 0
# # start_time = datetime.now()
# # OUTSIDER_COOLDOWN = 5
# # last_outsider_time = 0

# # while True:
# #     success, img = cap.read()
# #     if not success:
# #         continue

# #     frame_count += 1
# #     if frame_count % FRAME_SKIP != 0:
# #         continue

# #     imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
# #     imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

# #     facesCurFrame = face_recognition.face_locations(imgSmall)
# #     encodesCurFrame = face_recognition.face_encodings(imgSmall, facesCurFrame)

# #     now = datetime.now()
# #     current_time = time.time()
# #     detected_names = []

# #     outsider_detected = False  # Flag for Red LED + Buzzer

# #     for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
# #         face_distances = face_recognition.face_distance(known_encodings, encodeFace)
# #         if len(face_distances) != 0:
# #             best_match_index = np.argmin(face_distances)
# #             if face_distances[best_match_index] < STRICT_THRESHOLD:
# #                 name = classNames[best_match_index].upper()
# #             else:
# #                 name = "OUTSIDER"
# #         else:
# #             name = "OUTSIDER"

# #         y1, x2, y2, x1 = faceLoc
# #         y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
# #         color = (0,255,0) if name!="OUTSIDER" else (0,0,255)
# #         cv2.rectangle(img,(x1,y1),(x2,y2),color,2)
# #         cv2.putText(img,name,(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,color,2)

# #         # ===== OUTSIDER =====
# #         if name == "OUTSIDER":
# #             set_led_buzzer(green=0, red=1, buzzer=1)  # Red + Buzzer ON
# #             outsider_detected = True
# #             if current_time - last_outsider_time > OUTSIDER_COOLDOWN:
# #                 winsound.Beep(1500, 800)
# #                 speak("Alert! Outsider detected")
# #                 last_outsider_time = current_time
# #             continue

# #         # ===== KNOWN STUDENT =====
# #         detected_names.append(name)
# #         set_led_buzzer(green=1, red=0, buzzer=0)  # Green ON, Red & Buzzer OFF

# #         if name not in attendance_data or attendance_data[name]["status"] == "OUT":
# #             speak(f"{name} Enter")
# #             mark_attendance(name, now, "IN")

# #         last_seen[name] = current_time

# #     # ===== EXIT CHECK =====
# #     for name in list(attendance_data.keys()):
# #         if attendance_data[name]["status"] == "IN":
# #             if name not in detected_names:
# #                 time_gap = current_time - last_seen.get(name, 0)
# #                 if time_gap > EXIT_DELAY:
# #                     speak(f"{name} Exit")
# #                     mark_attendance(name, now, "OUT")
# #                     if name in last_seen:
# #                         del last_seen[name]

# #     # ===== TURN OFF RED/Buzzer IF OUTSIDER NOT DETECTED =====
# #     if not outsider_detected:
# #         set_led_buzzer(green=0, red=0, buzzer=0)

# #     cv2.imshow("Smart Attendance System", img)

# #     if (now - start_time).total_seconds() > PERIOD_DURATION:
# #         break

# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # # ==============================  
# # # FINAL ATTENDANCE WITH PRESENT / ABSENT
# # final_data = []

# # for name, data in attendance_data.items():
# #     if data["status"] == "IN":
# #         duration = (datetime.now() - data["last_entry"]).total_seconds()
# #         data["total_time"] += duration

# #     total_minutes = round(data["total_time"] / 60, 2)
# #     attendance_status = "PRESENT" if data["total_time"] >= MIN_REQUIRED_TIME else "ABSENT"

# #     final_data.append({
# #         "Name": name,
# #         "Date": data["date"],
# #         "Day": data["day"],
# #         "Entry_Time": data["entry_time"],
# #         "Exit_Time": data["exit_time"],
# #         "Total_Minutes": total_minutes,
# #         "Attendance_Status": attendance_status
# #     })

# # df = pd.DataFrame(final_data)
# # df.to_csv("attendance.csv", index=False)

# # cap.release()
# # cv2.destroyAllWindows()

# # print("Attendance saved successfully with Present/Absent status!")
# # set_led_buzzer(green=0, red=0, buzzer=0)  # Turn off all at end



# import cv2
# import numpy as np
# import face_recognition
# import os
# import pandas as pd
# from datetime import datetime
# import pyttsx3
# import threading
# from queue import Queue 
# import time
# import winsound
# import serial

# arduino = serial.Serial('COM5', 9600)
# time.sleep(2)

# def set_led_buzzer(green, red, buzzer):
#     cmd = f"{green},{red},{buzzer}\n"
#     arduino.write(cmd.encode())

# engine = pyttsx3.init()
# engine.setProperty('rate', 150)
# voice_queue = Queue()

# def voice_worker():
#     while True:
#         text = voice_queue.get()
#         if text is None:
#             break
#         engine.say(text)
#         engine.runAndWait()
#         voice_queue.task_done()

# threading.Thread(target=voice_worker, daemon=True).start()

# def speak(text):
#     voice_queue.put(text)

# PERIOD_DURATION = 50 * 60
# STRICT_THRESHOLD = 0.55
# FRAME_SKIP = 3
# EXIT_DELAY = 3
# MIN_REQUIRED_TIME = 40 * 60

# path = "dataset"
# images = []
# classNames = []

# # -------------------------------
# # LOAD ALL IMAGES FROM DATASET
# # -------------------------------

# for student_name in os.listdir(path):

#     student_folder = os.path.join(path, student_name)

#     if os.path.isdir(student_folder):

#         for img_file in os.listdir(student_folder):

#             img_path = os.path.join(student_folder, img_file)

#             img = cv2.imread(img_path)

#             if img is not None:

#                 images.append(img)

#                 classNames.append(student_name)

# print("Students Loaded:", set(classNames))


# def findEncodings(images, classNames):

#     encodeList = []
#     validClassNames = []

#     for img, name in zip(images, classNames):

#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#         encodes = face_recognition.face_encodings(img)

#         if len(encodes) > 0:

#             encodeList.append(encodes[0])

#             validClassNames.append(name)

#         else:

#             print(f"Encoding failed for {name}")

#     return encodeList, validClassNames


# known_encodings, classNames = findEncodings(images, classNames)

# print("Encoding Completed")


# attendance_data = {}
# last_seen = {}

# def mark_attendance(name, now, action):

#     if name not in attendance_data:

#         attendance_data[name] = {

#             "last_entry": None,
#             "total_time": 0,
#             "status": "OUT",
#             "date": now.strftime("%d-%m-%Y"),
#             "day": now.strftime("%A"),
#             "entry_time": None,
#             "exit_time": None
#         }

#     student = attendance_data[name]

#     if action == "IN":

#         student["last_entry"] = now

#         student["status"] = "IN"

#         if student["entry_time"] is None:

#             student["entry_time"] = now.strftime("%H:%M:%S")

#     elif action == "OUT" and student["status"] == "IN":

#         duration = (now - student["last_entry"]).total_seconds()

#         student["total_time"] += duration

#         student["status"] = "OUT"

#         student["exit_time"] = now.strftime("%H:%M:%S")


# # -------------------------------
# # CAMERA START
# # -------------------------------

# cap = cv2.VideoCapture(0)

# cap.set(3,1280)
# cap.set(4,720)

# print("Camera Started... Press Q to Stop")

# frame_count = 0

# start_time = datetime.now()

# OUTSIDER_COOLDOWN = 5

# last_outsider_time = 0


# while True:

#     success, img = cap.read()

#     if not success:
#         continue

#     frame_count += 1

#     if frame_count % FRAME_SKIP != 0:
#         continue

#     # -------------------------------
#     # FACE DETECTION (BETTER SIZE)
#     # -------------------------------

#     imgSmall = cv2.resize(img,(0,0),None,0.5,0.5)

#     imgSmall = cv2.cvtColor(imgSmall,cv2.COLOR_BGR2RGB)

#     facesCurFrame = face_recognition.face_locations(imgSmall)

#     encodesCurFrame = face_recognition.face_encodings(imgSmall,facesCurFrame)

#     now = datetime.now()

#     current_time = time.time()

#     detected_names = []

#     outsider_detected = False


#     for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):

#         name="OUTSIDER"

#         if len(known_encodings)>0:

#             matches = face_recognition.compare_faces(
#                 known_encodings,
#                 encodeFace,
#                 tolerance=STRICT_THRESHOLD
#             )

#             face_distances = face_recognition.face_distance(
#                 known_encodings,
#                 encodeFace
#             )

#             best_match_index = np.argmin(face_distances)

#             if matches[best_match_index] and face_distances[best_match_index] < STRICT_THRESHOLD:

#                 name = classNames[best_match_index].upper()


#         y1,x2,y2,x1 = faceLoc

#         y1,x2,y2,x1 = y1*2,x2*2,y2*2,x1*2


#         color=(0,255,0) if name!="OUTSIDER" else (0,0,255)

#         cv2.rectangle(img,(x1,y1),(x2,y2),color,2)

#         cv2.putText(img,name,(x1,y1-10),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.8,
#                     color,
#                     2)


#         if name=="OUTSIDER":

#             set_led_buzzer(0,1,1)

#             outsider_detected=True

#             if current_time-last_outsider_time>OUTSIDER_COOLDOWN:

#                 winsound.Beep(1500,800)

#                 speak("Alert outsider detected")

#                 last_outsider_time=current_time

#             continue


#         detected_names.append(name)

#         set_led_buzzer(1,0,0)

#         if name not in attendance_data or attendance_data[name]["status"]=="OUT":

#             speak(f"{name} Enter")

#             mark_attendance(name,now,"IN")

#         last_seen[name]=current_time


#     for name in list(attendance_data.keys()):

#         if attendance_data[name]["status"]=="IN":

#             if name not in detected_names:

#                 time_gap=current_time-last_seen.get(name,0)

#                 if time_gap>EXIT_DELAY:

#                     speak(f"{name} Exit")

#                     mark_attendance(name,now,"OUT")

#                     if name in last_seen:

#                         del last_seen[name]


#     if not outsider_detected:

#         set_led_buzzer(0,0,0)


#     cv2.imshow("Smart Attendance System",img)


#     if (now-start_time).total_seconds()>PERIOD_DURATION:
#         break


#     if cv2.waitKey(1)&0xFF==ord('q'):
#         break



# final_data=[]

# for name,data in attendance_data.items():

#     if data["status"]=="IN":

#         duration=(datetime.now()-data["last_entry"]).total_seconds()

#         data["total_time"]+=duration


#     total_minutes=round(data["total_time"]/60,2)

#     attendance_status="PRESENT" if data["total_time"]>=MIN_REQUIRED_TIME else "ABSENT"


#     final_data.append({

#         "Name":name,

#         "Date":data["date"],

#         "Day":data["day"],

#         "Entry_Time":data["entry_time"],

#         "Exit_Time":data["exit_time"],

#         "Total_Minutes":total_minutes,

#         "Attendance_Status":attendance_status
#     })


# df=pd.DataFrame(final_data)

# df.to_csv("attendance.csv",index=False)

# cap.release()

# cv2.destroyAllWindows()

# print("Attendance saved successfully!")

# set_led_buzzer(0,0,0)





# import cv2
# import numpy as np
# import face_recognition
# import os
# import pandas as pd
# from datetime import datetime
# import pyttsx3
# import threading
# from queue import Queue
# import time
# import winsound
# import serial
# import smtplib
# from email.message import EmailMessage

# arduino = serial.Serial('COM5', 9600)
# time.sleep(2)

# def set_led_buzzer(green, red, buzzer):
#     cmd = f"{green},{red},{buzzer}\n"
#     arduino.write(cmd.encode())

# engine = pyttsx3.init()
# engine.setProperty('rate', 150)
# voice_queue = Queue()

# def voice_worker():
#     while True:
#         text = voice_queue.get()
#         if text is None:
#             break
#         engine.say(text)
#         engine.runAndWait()
#         voice_queue.task_done()

# threading.Thread(target=voice_worker, daemon=True).start()

# def speak(text):
#     voice_queue.put(text)

# PERIOD_DURATION = 50 * 60
# STRICT_THRESHOLD = 0.55
# FRAME_SKIP = 3
# EXIT_DELAY = 3
# MIN_REQUIRED_TIME = 40 * 60

# path = "dataset"
# images = []
# classNames = []

# # LOAD DATASET
# for student_name in os.listdir(path):

#     student_folder = os.path.join(path, student_name)

#     if os.path.isdir(student_folder):

#         for img_file in os.listdir(student_folder):

#             img_path = os.path.join(student_folder, img_file)

#             img = cv2.imread(img_path)

#             if img is not None:
#                 images.append(img)
#                 classNames.append(student_name)

# print("Students Loaded:", set(classNames))


# def findEncodings(images, classNames):

#     encodeList = []
#     validClassNames = []

#     for img, name in zip(images, classNames):

#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#         encodes = face_recognition.face_encodings(img)

#         if len(encodes) > 0:
#             encodeList.append(encodes[0])
#             validClassNames.append(name)
#         else:
#             print(f"Encoding failed for {name}")

#     return encodeList, validClassNames


# known_encodings, classNames = findEncodings(images, classNames)

# print("Encoding Completed")

# attendance_data = {}
# last_seen = {}

# def mark_attendance(name, now, action):

#     if name not in attendance_data:

#         attendance_data[name] = {

#             "last_entry": None,
#             "total_time": 0,
#             "status": "OUT",
#             "date": now.strftime("%d-%m-%Y"),
#             "day": now.strftime("%A"),
#             "entry_time": None,
#             "exit_time": None
#         }

#     student = attendance_data[name]

#     if action == "IN":

#         student["last_entry"] = now
#         student["status"] = "IN"

#         if student["entry_time"] is None:
#             student["entry_time"] = now.strftime("%H:%M:%S")

#     elif action == "OUT" and student["status"] == "IN":

#         duration = (now - student["last_entry"]).total_seconds()
#         student["total_time"] += duration
#         student["status"] = "OUT"
#         student["exit_time"] = now.strftime("%H:%M:%S")


# # CAMERA START
# cap = cv2.VideoCapture(0)

# cap.set(3,1280)
# cap.set(4,720)

# print("Camera Started... Press Q to Stop")

# frame_count = 0
# start_time = datetime.now()

# OUTSIDER_COOLDOWN = 5
# last_outsider_time = 0

# while True:

#     success, img = cap.read()

#     if not success:
#         continue

#     frame_count += 1

#     if frame_count % FRAME_SKIP != 0:
#         continue

#     imgSmall = cv2.resize(img,(0,0),None,0.5,0.5)
#     imgSmall = cv2.cvtColor(imgSmall,cv2.COLOR_BGR2RGB)

#     facesCurFrame = face_recognition.face_locations(imgSmall)
#     encodesCurFrame = face_recognition.face_encodings(imgSmall,facesCurFrame)

#     now = datetime.now()
#     current_time = time.time()

#     detected_names = []
#     outsider_detected = False

#     for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):

#         name="OUTSIDER"

#         if len(known_encodings)>0:

#             matches = face_recognition.compare_faces(
#                 known_encodings,
#                 encodeFace,
#                 tolerance=STRICT_THRESHOLD
#             )

#             face_distances = face_recognition.face_distance(
#                 known_encodings,
#                 encodeFace
#             )

#             best_match_index = np.argmin(face_distances)

#             if matches[best_match_index] and face_distances[best_match_index] < STRICT_THRESHOLD:
#                 name = classNames[best_match_index].upper()

#         y1,x2,y2,x1 = faceLoc
#         y1,x2,y2,x1 = y1*2,x2*2,y2*2,x1*2

#         color=(0,255,0) if name!="OUTSIDER" else (0,0,255)

#         cv2.rectangle(img,(x1,y1),(x2,y2),color,2)

#         cv2.putText(img,name,(x1,y1-10),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.8,
#                     color,
#                     2)

#         if name=="OUTSIDER":

#             set_led_buzzer(0,1,1)
#             outsider_detected=True

#             if current_time-last_outsider_time>OUTSIDER_COOLDOWN:

#                 winsound.Beep(1500,800)
#                 speak("Alert outsider detected")
#                 last_outsider_time=current_time

#             continue

#         detected_names.append(name)

#         set_led_buzzer(1,0,0)

#         if name not in attendance_data or attendance_data[name]["status"]=="OUT":

#             speak(f"{name} Enter")
#             mark_attendance(name,now,"IN")

#         last_seen[name]=current_time


#     for name in list(attendance_data.keys()):

#         if attendance_data[name]["status"]=="IN":

#             if name not in detected_names:

#                 time_gap=current_time-last_seen.get(name,0)

#                 if time_gap>EXIT_DELAY:

#                     speak(f"{name} Exit")
#                     mark_attendance(name,now,"OUT")

#                     if name in last_seen:
#                         del last_seen[name]

#     if not outsider_detected:
#         set_led_buzzer(0,0,0)

#     cv2.imshow("Smart Attendance System",img)

#     if (now-start_time).total_seconds()>PERIOD_DURATION:
#         break

#     if cv2.waitKey(1)&0xFF==ord('q'):
#         break


# final_data=[]

# for name,data in attendance_data.items():

#     if data["status"]=="IN":

#         duration=(datetime.now()-data["last_entry"]).total_seconds()
#         data["total_time"]+=duration

#     total_minutes=round(data["total_time"]/60,2)

#     attendance_status="PRESENT" if data["total_time"]>=MIN_REQUIRED_TIME else "ABSENT"

#     final_data.append({

#         "Name":name,
#         "Date":data["date"],
#         "Day":data["day"],
#         "Entry_Time":data["entry_time"],
#         "Exit_Time":data["exit_time"],
#         "Total_Minutes":total_minutes,
#         "Attendance_Status":attendance_status
#     })


# df=pd.DataFrame(final_data)
# df.to_csv("attendance.csv",index=False)

# print("Attendance saved successfully!")

# # EMAIL SENDING
# def send_email():

#     sender_email = "smartattendance.ai@gmail.com"
#     sender_password = "kjgq ubse tayt hrlw"

#     receiver_emails = [
#         "vivekkumarsarai52@gmail.com",
#         "agrawaladitya2910@gmail.com",
#         "ayushsinha91532@gmail.com",
#         "garima.singh6201@gmail.com"
#     ]

#     msg = EmailMessage()

#     msg['Subject'] = "Smart Attendance Report"
#     msg['From'] = sender_email
#     msg['To'] = ", ".join(receiver_emails)

#     msg.set_content("Today's attendance report is attached.")

#     with open("attendance.csv","rb") as f:
#         msg.add_attachment(
#             f.read(),
#             maintype="application",
#             subtype="csv",
#             filename="attendance.csv"
#         )

#     server = smtplib.SMTP_SSL("smtp.gmail.com",465)
#     server.login(sender_email,sender_password)
#     server.send_message(msg)
#     server.quit()

#     print("Attendance email sent successfully!")

# send_email()

# cap.release()
# cv2.destroyAllWindows()
# set_led_buzzer(0,0,0)