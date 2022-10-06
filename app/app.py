import streamlit


def predict(image):
    return "Object", 0.25

def output_prediction_callback():
    prediction = predict(image=streamlit.session_state.image)
    output_column.write(f"Prédiction: '{prediction[0]}'")
    output_column.write(f"Confiance: {prediction[1]}")
    output_column.selectbox(label="Le modèle est-il correct?", options=("", "Oui", "Non"), key="answer", on_change=feedback_callback) 


def feedback_callback():
    if streamlit.session_state.answer == "Non":
        output_column.text_input("Veuillez proposer la bonne classe:", key='correct_class')
    save_feedback()


def save_feedback():
    with open("test.csv", "w") as corrections_file:
        corrections_file.write(streamlit.session_state.answer)


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
 