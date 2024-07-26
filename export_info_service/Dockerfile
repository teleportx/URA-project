FROM python:3.10-slim-buster

WORKDIR /app

COPY ../requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


COPY .. .

WORKDIR /app/export_info_service
CMD ["python3.10", "-m", "main"]
