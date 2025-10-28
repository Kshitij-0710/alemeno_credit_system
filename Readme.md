# Submission Round: Credit approval system

## Getting started

docker-compose up --build -d

Builds the images and starts the django, postgres, and redis containers.

## Data ingestion

docker-compose exec web python manage.py ingest_data

Queues a background task to ingest customer and loan data from the excel files.

## API endpoints

The api documentation is auto-generated and available via redoc on this url:
http://localhost:8000/docs/
