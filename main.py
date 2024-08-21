import cv2
import os
from helpers import img_list_generator
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials , db , storage
import os 
from datetime import datetime


cred = credentials.Certificate(r"C:\Users\bedir\OneDrive\Masaüstü\YMIR\PROJECTS\PYTHON\AI\FACE_RECOGNITION\FACE_RECOGNITION\firebase_cred.json")
firebase_admin.initialize_app(cred,{
    "databaseURL":"https://faceattendacerealtime-d07fe-default-rtdb.firebaseio.com/",
    "storageBucket":"faceattendacerealtime-d07fe.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)  # index 0
cap.set(3, 640)  # Set width
cap.set(4, 480)   # Set height


if not cap.isOpened():
    print("Error: Camera not opened.")
    exit() 

img_background = cv2.imread("Resources\\background.png")

if img_background is None:
    print("Error: Background image not loaded.")
    exit()

img_modes_list = img_list_generator("Resources\\Modes")

with open("EncodeFile.p","rb") as file:
    encode_list_known_with_ids = pickle.load(file)

encode_list_known,user_ids = encode_list_known_with_ids

mode_type = 0
match_id = -1
counter = 0
img_user = []

while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to capture image.")
        break

    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)
    
    face_cur_frame = face_recognition.face_locations(imgS)
    encode_cur_frame = face_recognition.face_encodings(imgS,face_cur_frame)

    img_background[162:642,55:695] = img
    img_background[44:677,808:1222] = img_modes_list[mode_type]
    
    if face_cur_frame:
        for encode_face,face_loc in zip(encode_cur_frame,face_cur_frame):
            matches = face_recognition.compare_faces(encode_list_known,encode_face)
            face_dist = face_recognition.face_distance(encode_list_known,encode_face)
            # print(f" matches : {matches}\n dist : {face_dist}")
            match_indx = np.argmin(face_dist)
            # print(f" index : {match_indx} ")
            
            if matches[match_indx]:
                match_id = user_ids[match_indx]
                #print(f"qFace Detected . ID : {match_id}")
                y1,x2,y2,x1 = face_loc
                y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                bbox = 55+x1,162+y1,x2-x1,y2-y1

                img_background = cvzone.cornerRect(img_background,bbox,rt=0)
                if counter ==0:
                    cvzone.putTextRect(img_background,"Loading...",(275,400))
                    cv2.imshow("Face Attendance", img_background)
                    cv2.waitKey(1)
                    counter=1
                    mode_type=1
        
        if counter != 0:
            if counter ==1:
                ref = db.reference(f"Users/{match_id}")
                user_info = ref.get()
                #print(user_info)
                blob = bucket.get_blob(f"images/{match_id}.jpg")
            
                if blob is None:
                    blob = bucket.get_blob(f"images/{match_id}.jpeg")

                if blob is not None:
                    arr = np.frombuffer(blob.download_as_string(), np.uint8)
                    img_user = cv2.imdecode(arr, cv2.COLOR_BGRA2BGR)
                    img_user = cv2.resize(img_user, (216, 216), interpolation=cv2.INTER_AREA)
                else:
                    print(f"Error: No image found for match ID {match_id}.")
                    img_user = cv2.imread("Resources/placeholder.png")  # Yedek bir resim göstermek için
                    img_user = cv2.resize(img_user, (216, 216), interpolation=cv2.INTER_AREA)
                date_format = "%Y-%m-%d %H:%M:%S"
                datetime_object = datetime.strptime(user_info["last_attendance_time"],date_format)
                current_time = datetime.now().strftime(date_format)
                seconds_elapsed = (datetime.now() - datetime_object).total_seconds()
                #print(seconds_elapsed)
                if seconds_elapsed >30:
                    user_info["total_attendance"] +=1
                    ref.child("total_attendance").set(user_info["total_attendance"]) 
                    ref.child("last_attendance_time").set(current_time)
                else:
                    mode_type = 3
                    counter = 0
                    img_background[44:677,808:1222] = img_modes_list[mode_type]
            
            if mode_type !=3:

                if 10<counter<20:
                    mode_type=2
                
                img_background[44:677,808:1222] = img_modes_list[mode_type]

                if counter<=10:
                    cv2.putText(img_background,str(user_info["total_attendance"]),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    (w,h),_ = cv2.getTextSize(str(user_info["name"]),cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414-w)// 2
                    cv2.putText(img_background,str(user_info["name"]),(808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),1)
                    cv2.putText(img_background,str(user_info["major"]),(1006,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(img_background,str(match_id),(1006,493),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(img_background,str(user_info["standing"]),(910,625),cv2.FONT_HERSHEY_COMPLEX,0.6 ,(0,0,0),1)
                    cv2.putText(img_background,str(user_info["year"]),(1025,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,0,0),1)
                    cv2.putText(img_background,str(user_info["starting_year"]),(1125,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(0,0,0),1)

                    img_background[175:175+216,909:909+216]  = img_user
                
                if counter>=20:
                    counter = 0
                    mode_type = 0
                    user_info = []
                    img_user = []
                    img_background[44:677,808:1222] = img_modes_list[mode_type]


            counter+=1
    else:
            mode_type = 0
            counter = 0
            img_background[44:677,808:1222] = img_modes_list[mode_type]

    #cv2.imshow("Webcamera", img)
    cv2.imshow("Face Attendance", img_background)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit if 'q' is pressed
        break

cap.release()
cv2.destroyAllWindows()
