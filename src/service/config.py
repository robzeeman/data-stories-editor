import os

local_data: str = "/Users/robzeeman/Documents/DI_code/data_stories/data-stories-editor/src/service/data/"
max_content_length: int = 16 * 1024 * 1024

data = os.environ.get("DATA_DIR", local_data)
