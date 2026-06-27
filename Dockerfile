FROM  python:3.11-slim

WORKDIR /app

COPY ./service/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./service/ /app/service/

CMD ["fastapi", "run", "service/main.py", "--port", "80"]