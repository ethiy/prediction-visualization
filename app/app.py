import streamlit

def use_uploader(uploader):
    return uploader.file_uploader(label="Mettez une image de votre choix", type=["png", "jpeg", "jpg"])


def predict(image):
    return "Object", 0.25



def main():
    streamlit.set_page_config(layout="wide")
    streamlit.title("Visualisation de résultats de classifications.")
    input_column, output_column = streamlit.columns(spec=2, gap="medium")
    predict_button = False
    upload = True
    answer = ""
    with input_column:
        streamlit.header("Image d'entrée")
        uploader = streamlit.empty()
        if upload:
            uploaded_file = use_uploader(uploader)
            upload = False
        if uploaded_file is not None:
            image = uploaded_file.read()
            streamlit.image(image=image, use_column_width=True)
            uploader.empty()
    with output_column:
        streamlit.header("Prédiction")
        predict_button = streamlit.button("Prédire")
        label = streamlit.empty()
        confidence = streamlit.empty()
        feedback = streamlit.empty()
        if predict_button and answer == "":
            prediction = predict(image=image)
            label.write(f"Prédiction: '{prediction[0]}'")
            confidence.write(f"Confiance: {prediction[1]}")
            answer = feedback.selectbox(label="Le modèle est-il correct?", options=("", "Oui", "Non")) 
        else:
            label.write("Prédiction: ''")
            confidence.write("Confiance: ")
        


if __name__ == "__main__":
    main()
