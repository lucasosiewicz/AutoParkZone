import cv2
import torch
import easyocr
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

from scan.scanner import Scanner



YOLO = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, verbose=False)
EASYORC = easyocr.Reader(['en'])

scanner = Scanner(YOLO, EASYORC)




    

if __name__ == '__main__':
    inference = scanner('src/notebooks/data/cars_train/cars_train/02185.jpg')
    print(inference)