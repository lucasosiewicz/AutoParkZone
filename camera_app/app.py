import os
import numpy as np
from PIL import Image
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from ultralytics import YOLO
from easyocr import Reader

detector = YOLO('../model/plates_YOLO.pt')
reader = Reader(['en'])

load_dotenv()
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_URL = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

st.title('Camera App')
st.write('This is a simple web app which show you how my car plates detecion system works.')
st.write('To start, take a picture of a car plate and upload it below:')

uploaded_file = st.file_uploader("Choose a file", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.write('Here is the image you uploaded:')
    st.image(image, use_column_width=True)

    st.write('Next we will run the image through the car plates detection system.')
    st.write('This may take a few seconds...')

    # One-shot
    results = detector(image)
    if not Path("output/").exists():
        Path("output/").mkdir()

    # Fetching the most confident result
    if len(results) == 1:
        results = results[0]
    elif len(results) == 0:
        st.write('No car plates were found in the image.')
    else:
        max_conf = 0
        for result in results:
            if result['confidence'] > max_conf:
                max_conf = result['confidence']
                best_result = result

        results = best_result
    
    # saving the image with the bounding box
    results.save("output/inference.jpg")

    # Saving coordinates of the bounding box
    x, y, w, h = results.boxes.xywh.squeeze().round().int().tolist()

    inference_image = Image.open("output/inference.jpg")
    st.image(inference_image, use_column_width=True)

    st.write('Then image is cropped to the bounding box and passed to the OCR system.')
    inference_image = inference_image.crop((x-(w//2), y-(h//2), x+(w//2), y+(h//2)))
    st.image(inference_image, use_column_width=True)

    result_ocr = reader.readtext(np.array(inference_image),
                                 allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                                 detail=0,
                                 width_ths=0.9,
                                 slope_ths=0.5)
    st.write(f'The OCR system found the following text: {result_ocr[0]}')

    st.write('And that is how the car plates detection system works!')
    st.write('Now the result is saved to the database and you can check it in the app dashboard.')  

    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text(f"INSERT INTO currently_on (plate_code, arrives_at) VALUES ('{result_ocr[0]}', NOW())"))
        conn.commit()