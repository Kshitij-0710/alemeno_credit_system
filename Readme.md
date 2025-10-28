Credit approval system

getting started
docker-compose up --build -d

builds the images and starts the django, postgres, and redis containers.

docker-compose exec web python manage.py ingest_data
queues a background task to ingest customer and loan data from the excel files.

api endpoints
the api documentation is auto-generated and available via redoc on this url:
http://localhost:8000/docs/
