from pydantic import Json, BaseModel


class UrlType(BaseModel):
    url: str


class SettingStatus(BaseModel):
    id: str
    status: str


class UserRights(BaseModel):
    uuid: str
    eppn: str
    rights: str


class DataStory(BaseModel):
    datastory_id: str
    datastory_title: str
    datastory: Json


