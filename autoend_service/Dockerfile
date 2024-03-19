FROM python:3.10-slim-buster

WORKDIR /app

COPY ../requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


COPY ./autoend_service .

COPY ../utils utils
COPY ../keyboards keyboards
COPY ../db db
COPY ../config.py config.py
COPY ../setup_logger.py setup_logger.py
COPY ../.env .env

CMD ["python3.10", "-m", "main"]
