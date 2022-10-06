FROM python:3.9
COPY . /prediction-visualization
WORKDIR /prediction-visualization
RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["streamlit", "run", "app/app.py", "--server.port=8080"]
