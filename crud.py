from sqlalchemy.orm import Session
from sqlalchemy import func

import model, schemas

def create_book(db: Session, book: schemas.Book):
    db_book = model.Book(title=book.title, author=book.author, summary=book.summary, cover_url = book.cover_url)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_all_books(db: Session, limit:int = 10):
    return db.query(model.Book).limit(limit).all()

def get_books_by_title(db: Session, title: str):
    query = db.query(model.Book).filter(func.lower(model.Book.title).like(func.lower(f"%{title}%")))
    return query.first()