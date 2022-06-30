import datetime

from pydantic import BaseModel


class InfoFilesOut(BaseModel):
    request_code: int
    file_name: str
    date_created: datetime.datetime

    class Config:
        orm_mode = True


class GetImageOut(BaseModel):
    file_name: str
    date_created: datetime.datetime

    class Config:
        orm_mode = True
