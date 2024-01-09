from typing import Union
from pydantic import BaseModel

class BookBase(BaseModel):
    title: str
    author: str
    summary: Union[str, None]
    cover_url: str

class Book(BookBase):

    class Config:
        orm_mode = True


