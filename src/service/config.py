from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    local_data: str = "/Users/robzeeman/Documents/DI_code/data_stories/data-stories-editor/src/service/data/"
    max_content_length: int = 16 * 1024 * 1024
