import cv2
import os

def img_list_generator(folder_path):
    img_path = os.listdir(folder_path)
    img_list = [cv2.imread(os.path.join(folder_path,path)) for path in img_path]
    return img_list

def user_id_generator(folder_path):
    file_path = os.listdir(folder_path)
    id_list = [os.path.splitext(path)[0] for path in file_path]
    return id_list