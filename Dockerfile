FROM python:3.13-alpine

WORKDIR /app

COPY ./service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./service/ /app/service/

CMD ["fastapi", "run", "service/main.py", "--port", "80"]