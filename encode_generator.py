import cv2
import face_recognition
import pickle
from helpers import img_list_generator,user_id_generator

img_list =img_list_generator("FACE_RECOGNITION\\images")
user_ids = user_id_generator("FACE_RECOGNITION\\images")

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