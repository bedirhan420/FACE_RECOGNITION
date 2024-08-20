import cv2
import os
from helpers import img_list_generator

cap = cv2.VideoCapture(0)  # index 0
cap.set(3, 640)  # Set width
cap.set(4, 480)   # Set height


if not cap.isOpened():
    print("Error: Camera not opened.")
    exit()

img_background = cv2.imread("FACE_RECOGNITION/Resources/background.png")

if img_background is None:
    print("Error: Background image not loaded.")
    exit()

img_modes_list = img_list_generator("FACE_RECOGNITION\\Resources\\Modes")

while True:
    success, img = cap.read()
    if not success:
        print("Error: Failed to capture image.")
        break

    img_background[162:642,55:695] = img
    img_background[44:677,808:1222] = img_modes_list[0]
    
    #cv2.imshow("Webcamera", img)
    cv2.imshow("Face Attendance", img_background)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit if 'q' is pressed
        break

cap.release()
cv2.destroyAllWindows()
