from ultralytics import YOLO
from PIL import Image
import streamlit as st
import io


model = YOLO("yolo_trained.pt")

st.image("logo_coinche.png")
st.title("Detection d'objets")

picture = st.camera_input ("Take a picture")

uploaded_files = st.file_uploader(
    "Choose a CSV file", accept_multiple_files=True
)


for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    st.write("filename:", uploaded_file.name)
    st.write(bytes_data)

if picture :
    image = Image.open(picture )
    results = model(image)
    result_image = results[0].plot()
    result_image_pil = Image.fromarray(result_image)
    st.image(result_image_pil, caption='Object detection result')




