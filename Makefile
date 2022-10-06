.PHONY: run run-container gcloud-deploy

APP_NAME ?= prediction-visualization

run:
	@streamlit run app.py --server.port=8080

run-container:
	@docker build . -t ${APP_NAME}
	@docker run -e GOOGLE_APPLICATION_CREDENTIALS=/prediction-visualization/credentials/nth-record-364713-6376986faf0f.json -p 8080:8080 ${APP_NAME}

gcloud-deploy:
	@gcloud app deploy app.yaml
