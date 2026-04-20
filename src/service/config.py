import os

max_content_length: int = 16 * 1024 * 1024

DATA_LOCATION = "/app/service/data"
ds_app_url = os.environ.get("APP_DOMAIN", 'http://localhost')

