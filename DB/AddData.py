import firebase_admin
from firebase_admin import credentials , db

cred = credentials.Certificate(r"C:\Users\bedir\OneDrive\Masaüstü\YMIR\PROJECTS\PYTHON\AI\FACE_RECOGNITION\FACE_RECOGNITION\firebase_cred.json")
firebase_admin.initialize_app(cred,{
    "databaseURL":"https://faceattendacerealtime-d07fe-default-rtdb.firebaseio.com/"
})

ref = db.reference("Users")

data = {
    "123456":{
        "name":"Hugh Jackman",
        "major":"Wolverine",
        "starting_year":1968,
        "total_attendance":0,
        "standing":"G",
        "year":4,
        "last_attendance_time":"2024-12-11 00:54:34"
    },
    "321654":{
        "name":"Mehmet Ali Ozek",
        "major":"Full Stack",
        "starting_year":2003,
        "total_attendance":0,
        "standing":"G",
        "year":5,
        "last_attendance_time":"2024-12-11 00:54:34"
    },
    "456123":{
        "name":"Ryan Reynolds",
        "major":"Deadpool",
        "starting_year":1976,
        "total_attendance":0,
        "standing":"G",
        "year":4,
        "last_attendance_time":"2024-12-11 00:54:34"
    },
    "987654":{
        "name":"Bedirhan Celik",
        "major":"Admin",
        "starting_year":2004,
        "total_attendance":0,
        "standing":"G",
        "year":4,
        "last_attendance_time":"2024-12-11 00:54:34"
    }
}

for key,value in data.items():
    ref.child(key).set(value)