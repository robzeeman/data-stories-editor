from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    upload_folder: str = "/Users/robzeeman/Documents/DI_code/data_stories/oidc_service/data/"
    max_content_length: int = 16 * 1024 * 1024
