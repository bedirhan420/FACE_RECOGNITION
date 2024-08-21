import cv2
import face_recognition
import pickle
from helpers import img_list_generator,user_id_generator
import firebase_admin
from firebase_admin import credentials , db , storage
import os 

cred = credentials.Certificate(r"C:\Users\bedir\OneDrive\Masaüstü\YMIR\PROJECTS\PYTHON\AI\FACE_RECOGNITION\FACE_RECOGNITION\firebase_cred.json")
firebase_admin.initialize_app(cred,{
    "databaseURL":"https://faceattendacerealtime-d07fe-default-rtdb.firebaseio.com/",
    "storageBucket":"faceattendacerealtime-d07fe.appspot.com"
})

img_list =img_list_generator("images")
user_ids = user_id_generator("images")

path_list = os.listdir("images")

for path in path_list:
    file_name = f"images/{path}"
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)

def find_encodings(image_list):
    encode_list = []
    for img in image_list:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)
    
    return encode_list

print("Encoding Started ...")
encode_list_known = find_encodings(img_list)
encode_list_known_with_ids = [encode_list_known,user_ids]
print("Encoding Complete.")

with open("EncodeFile.p","wb") as file:
    pickle.dump(encode_list_known_with_ids,file)
print("File Saved.")