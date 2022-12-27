docker build . -t prediction-visualization 
docker run --rm -e GOOGLE_APPLICATION_CREDENTIALS=/prediction-visualization/credentials/prediction-visualisation-a42d739e5fc7.json -p 8080:8080 prediction-visualization
