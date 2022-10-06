import os
from pathlib import Path
import streamlit
from google.api_core.client_options import ClientOptions
import googleapiclient.discovery

import tensorflow as tf
import numpy as np

from imagenet_classnames import IMAGENET_CLASSNAMES


GOOGLE_AI_PLATFORM_ENDPOINT = "https://europe-west4-ml.googleapis.com"
GOOGLE_PROJECT_ID = "nth-record-364713"
MODEL = "resnet_101_imagenet"


def preprocess_image(image):
    return tf.expand_dims(tf.image.resize(tf.io.decode_image(image, channels=3), [224, 224]), axis=0)

def local_predict(image):
    resnet = tf.keras.models.load_model("models/resnet")
    return resnet.predict(image)


def cloud_predict(image):
    client_options = ClientOptions(api_endpoint=GOOGLE_AI_PLATFORM_ENDPOINT)
    ml_resource = googleapiclient.discovery.build("ml", "v1", cache_discovery=False, client_options=client_options).projects()
    model_path = f"projects/{GOOGLE_PROJECT_ID}/models/{MODEL}"
    image = tf.cast(image, tf.int16)
    request = ml_resource.predict(
        name=model_path,
        body={
            "signature_name": "serving_default",
            "instances": image.numpy().tolist()
        } 
    )
    response = request.execute()
    if "error" in response:
        output_column.error(response["error"])
    return response["predictions"]


@streamlit.cache
def predict(image):
    processed_image = preprocess_image(image)
    predictions = cloud_predict(processed_image)
    return IMAGENET_CLASSNAMES[np.argmax(predictions)], tf.reduce_max(np.max(predictions))


def output_prediction_callback():
    prediction = predict(image=streamlit.session_state.image)
    streamlit.session_state.predicted_class = prediction[0]
    streamlit.session_state.confidence = prediction[1]
    output_column.write(f"Prédiction: '{streamlit.session_state.predicted_class}'")
    output_column.write(f"Confiance: {streamlit.session_state.confidence}")
    output_column.selectbox(label="Le modèle est-il correct?", options=("", "Oui", "Non"), key="answer", on_change=feedback_callback) 


def feedback_callback():
    streamlit.session_state.feedback = streamlit.session_state.answer == "Non"
    with open("feedback.csv", "a") as corrections_file:
        corrections_file.write(streamlit.session_state.predicted_class + ", " + str(float(streamlit.session_state.confidence)) + ", " + str(streamlit.session_state.feedback))


streamlit.set_page_config(layout="wide")
streamlit.title("Visualisation de résultats de classifications.")
input_column, output_column = streamlit.columns(spec=2, gap="medium")
streamlit.session_state.uploaded_file = None
streamlit.session_state.image = None
input_column.header("Image d'entrée")
streamlit.session_state.uploaded_file = input_column.file_uploader(label="Mettez une image de votre choix", type=["png", "jpeg", "jpg"])
if streamlit.session_state.uploaded_file is not None:
    streamlit.session_state.image = streamlit.session_state.uploaded_file.read()
    input_column.image(image=streamlit.session_state.image, use_column_width=True)

output_column.header("Prédiction")
predict_button = output_column.empty()
if streamlit.session_state.image is not None:
    streamlit.session_state.predict = predict_button.button("Prédire", on_click=output_prediction_callback)    
 