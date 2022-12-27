FROM python:3.9
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /prediction-visualization
WORKDIR /prediction-visualization
EXPOSE 8080
ENTRYPOINT ["streamlit", "run", "app/app.py", "--server.port=8080"]
