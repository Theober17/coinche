from ultralytics import YOLO
import streamlit as st
from PIL import Image

model = YOLO("best.pt")

st.title("Detection de cartes")

picture = st.camera_input("Take a picture")

if picture :
    image = Image.open(picture)
    results = model(image)
    result_image = results[0].plot()
    result_image_pil = Image.fromarray(result_image)
    st.image(result_image_pil, caption='Resultat de la detection', channels="BGR")
    
