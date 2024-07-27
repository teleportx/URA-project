FROM python:3.10-slim-buster

WORKDIR /app

COPY ../requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


COPY .. .

WORKDIR /app/api_services/srat_service
CMD ["fastapi", "run", "main.py", "--port", "80"]
