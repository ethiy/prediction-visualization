.PHONY: run run-container gcloud-deploy

APP_NAME ?= prediction-visualization

run:
	@streamlit run app.py --server.port=8080

run-container:
	@docker build . -t ${APP_NAME}
	@docker run -e GOOGLE_APPLICATION_CREDENTIALS=/prediction-visualization/credentials/prediction-visualisation-a42d739e5fc7.json -p 8080:8080 ${APP_NAME}

gcloud-deploy:
	@gcloud app deploy app.yaml
