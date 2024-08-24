from flask import Flask, request, jsonify
import cv2
import face_recognition
import pickle
import numpy as np
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime
import os
from dotenv import load_dotenv
from enums import HttpStatusCodes

load_dotenv()

firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
firebase_database_url = os.getenv("FIREBASE_DATABASE_URL")
firebase_storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")

cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred, {
    "databaseURL": firebase_database_url,
    "storageBucket": firebase_storage_bucket
})

bucket = storage.bucket()
ref = db.reference("Users")

app = Flask(__name__)

@app.route('/addUser', methods=['POST'])
def add_user():
    data = request.form.get('data')
    if data:
        data = eval(data)
    else:
        return jsonify({"error": "JSON data is required"}), HttpStatusCodes.BAD_REQUEST.value

    name = data['name']
    major = data['major']
    year = int(data['year'])
    starting_year = int(data['starting_year'])
    img_file = request.files['image']

    user_id = os.path.splitext(img_file.filename)[0]

    img_content = img_file.read()
    
    img = face_recognition.load_image_file(img_file)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(img_rgb)[0]

    blob = bucket.blob(f'images/{user_id}.jpg')
    blob.upload_from_string(img_content, content_type=img_file.content_type)

    user_data = {
        "name": name,
        "major": major,
        "year": year,
        "starting_year": starting_year,
        "total_attendance": 0,
        "standing": "G",
        "last_attendance_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    ref.child(user_id).set(user_data)

    with open("EncodeFile.p", "rb") as file:
        encode_list_known_with_ids = pickle.load(file)
    
    encode_list_known_with_ids[0].append(encode)
    encode_list_known_with_ids[1].append(user_id)
    
    with open("EncodeFile.p", "wb") as file:
        pickle.dump(encode_list_known_with_ids, file)
    
    return jsonify({"message": "User added successfully", "user_id": user_id}), HttpStatusCodes.CREATED.value


@app.route('/updateUser/<user_id>', methods=['PUT'])
def update_user(user_id):
    updated_data = request.json

    user_ref = ref.child(user_id)
    user_info = user_ref.get()

    if not user_info:
        return jsonify({"error": "User not found"}), HttpStatusCodes.NOT_FOUND.value

    user_ref.update(updated_data)
    return jsonify({"message": "User updated successfully"}), HttpStatusCodes.OK.value

@app.route('/deleteUser<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user_ref = ref.child(user_id)
    user_info = user_ref.get()

    if not user_info:
        return jsonify({"error": "User not found"}),  HttpStatusCodes.NOT_FOUND.value

    user_ref.delete()

    blob = bucket.blob(f'images/{user_id}.jpg')
    if blob.exists():
        blob.delete()

    with open("EncodeFile.p", "rb") as file:
        encode_list_known_with_ids = pickle.load(file)
    
    if user_id in encode_list_known_with_ids[1]:
        index = encode_list_known_with_ids[1].index(user_id)
        encode_list_known_with_ids[0].pop(index)
        encode_list_known_with_ids[1].pop(index)
    
    with open("EncodeFile.p", "wb") as file:
        pickle.dump(encode_list_known_with_ids, file)

    return jsonify({"message": "User deleted successfully"}), HttpStatusCodes.NO_CONTENT.value

@app.route('/getUsers', methods=['GET'])
def get_users():
    users = ref.get()
    return jsonify(users), HttpStatusCodes.OK.value

@app.route('/faceRecognition', methods=['POST'])
def face_recognition_api():
    img_file = request.files['image']
    img = face_recognition.load_image_file(img_file)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(img_rgb)[0]

    with open("EncodeFile.p", "rb") as file:
        encode_list_known_with_ids = pickle.load(file)

    encode_list_known, user_ids = encode_list_known_with_ids

    matches = face_recognition.compare_faces(encode_list_known, encode)
    face_dist = face_recognition.face_distance(encode_list_known, encode)
    match_index = np.argmin(face_dist)

    if matches[match_index]:
        match_id = user_ids[match_index]
        user_info_ref = ref.child(match_id)
        user_info = user_info_ref.get()

        updated_data = {
            "total_attendance": user_info.get("total_attendance", 0) + 1,
            "last_attendance_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        user_info_ref.update(updated_data)
        user_info = user_info_ref.get()

        return jsonify({"match": True, "user_id": match_id, "user_info": user_info}), HttpStatusCodes.OK.value
    else:
        return jsonify({"match": False}), HttpStatusCodes.NOT_FOUND.value


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
