from functools import lru_cache
import os
from pathlib import Path
from unittest import result
import streamlit
from google.api_core.client_options import ClientOptions
import googleapiclient.discovery

import tensorflow as tf
import numpy as np
import pandas as pd

from soccer_classnames import CLASSNAMES


GOOGLE_AI_PLATFORM_ENDPOINT = "https://europe-west3-ml.googleapis.com"
GOOGLE_PROJECT_ID = "prediction-visualisation"
MODEL = "resnet_101_imagenet"

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "./credentials/prediction-visualisation-a42d739e5fc7.json"


def preprocess_image(image):
    return tf.expand_dims(
        tf.image.resize(tf.io.decode_image(image, channels=3), [224, 224]), axis=0
    )


def local_predict(image):
    resnet = tf.keras.models.load_model("models/resnet_fine_tuned")
    return resnet.predict(image)


def cloud_predict(image):
    client_options = ClientOptions(api_endpoint=GOOGLE_AI_PLATFORM_ENDPOINT)
    ml_resource = googleapiclient.discovery.build(
        "ml", "v1", cache_discovery=False, client_options=client_options
    ).projects()
    model_path = f"projects/{GOOGLE_PROJECT_ID}/models/{MODEL}"
    image = tf.cast(image, tf.int16)
    request = ml_resource.predict(
        name=model_path,
        body={"signature_name": "serving_default", "instances": image.numpy().tolist()},
    )
    response = request.execute()
    if "error" in response:
        output_column.error(response["error"])
    result = []
    for score_list in response["predictions"]:
        for score in score_list:
            result.append(score)
    return result


def predict(image):
    processed_image = preprocess_image(image)
    predictions = cloud_predict(processed_image)
    descending_index_order = np.argsort(predictions)[-5:]
    result = []
    for i in reversed(descending_index_order):
        result.append((CLASSNAMES[i], float(predictions[i])))
    return pd.DataFrame(result, columns=["Classe", "Confiance"])


streamlit.set_page_config(layout="wide")
streamlit.title("Visualisation de résultats de classifications.")
input_column, output_column = streamlit.columns(spec=2, gap="medium")
streamlit.session_state.uploaded_file = None
streamlit.session_state.image = None
streamlit.session_state.predict = None
streamlit.session_state.answer = ""
input_column.header("Image d'entrée")
streamlit.session_state.uploaded_file = input_column.file_uploader(
    label="Mettez une image de votre choix", type=["png", "jpeg", "jpg"]
)
if streamlit.session_state.uploaded_file is not None:
    streamlit.session_state.image = streamlit.session_state.uploaded_file.read()
    input_column.image(image=streamlit.session_state.image, use_column_width=True)

output_column.header("Prédiction")
predict_button = output_column.empty()
if streamlit.session_state.image is not None:
    streamlit.session_state.predict = predict_button.button("Prédire")
if streamlit.session_state.predict:
    streamlit.session_state.prediction = predict(image=streamlit.session_state.image)
    output_column.write("Prédiction:")
    output_column.write(streamlit.session_state.prediction)
    output_column.selectbox(
        label="Corrigez la classe si le résultat est faux :",
        options=("",) + tuple(CLASSNAMES),
        key="answer",
    )
if streamlit.session_state.answer != "":
    with open("feedback.csv", "a") as corrections_file:
        corrections_file.write(
            streamlit.session_state.prediction["Classe"][0]
            + ", "
            + str(float(streamlit.session_state.prediction["Confiance"][0]))
            + ", "
            + streamlit.session_state.answer
            + "\n"
        )
