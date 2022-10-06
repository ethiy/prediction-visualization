docker build . -t prediction-visualization 
docker run --rm -e GOOGLE_APPLICATION_CREDENTIALS=/prediction-visualization/credentials/nth-record-364713-6376986faf0f.json -p 8080:8080 prediction-visualization
