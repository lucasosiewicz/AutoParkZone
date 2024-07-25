import os
import cv2
import torch
import easyocr
import tempfile
import numpy as np
import streamlit as st

from scan.scanner import Scanner


if __name__ == '__main__':
    # Load the image in streamlit app
    data = st.file_uploader('Upload an image', type=['jpg', 'png', 'jpeg'])

    # If the file is uploaded
    if data is not None:
        
        # Load the models
        YOLO = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, verbose=False)
        EASYORC = easyocr.Reader(['en'])

        # Initialize plate scanner
        scanner = Scanner(YOLO, EASYORC)

        # Display the image and logs
        st.image(data)
        st.write('File uploaded')
        st.write('Inference:')

        # Create a temporary file to store the image
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(data.read())
            temp_file_path = temp_file.name
        # Make an inference
        st.write(scanner(temp_file_path))
        
        # Remove the temporary file
        os.remove(temp_file_path)
