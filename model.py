from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from db import Base


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    author = Column(String(255))
    summary = Column(Text, nullable=True)
    cover_url = Column(String(255))
