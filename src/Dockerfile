FROM python:3.14

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./service /app/service

CMD ["fastapi", "run", "service/main.py", "--port", "80"]