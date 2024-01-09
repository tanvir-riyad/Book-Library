from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
import requests
from sqlalchemy import create_engine
from model import Book, Base
from db import get_db, engine
import schemas
import crud
from typing import List


app = FastAPI()

Base.metadata.create_all(bind=engine)


def is_isbn_valid(isbn):

    "Check if the given isbn is valid or not"

    if not isinstance(isbn, str) or not isbn.isdigit():
        return False

    if len(isbn) not in {10, 13}:
        return False

    if len(isbn) == 10:
        total = sum(int(digit) * weight for digit, weight in zip(isbn[:-1], range(10, 0, -1)))
        check_digit = 11 - (total % 11)
        check_digit = 'X' if check_digit == 10 else str(check_digit)
        return check_digit == isbn[-1]

    if len(isbn) == 13:
        total = sum(int(digit) * (1 if i % 2 == 0 else 3) for i, digit in enumerate(isbn[:-1]))
        check_digit = 10 - (total % 10)
        check_digit = 0 if check_digit == 10 else check_digit
        return check_digit == int(isbn[-1])

    return True


@app.get("/isbn/{isbn}", response_model=dict)
def get_book_details(isbn: str):
    """
    Get book details by ISBN.

    Returns:
        dict: Book details including author, title, summary, and cover URL.
    """

    if not is_isbn_valid(isbn):
        raise HTTPException(status_code=400, detail="ISBN is not valid")
    OPEN_URL = f"http://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=data&format=json"
    response = requests.get(OPEN_URL)
    Works_URL = f"https://openlibrary.org/isbn/{isbn}.json"
    works_request = requests.get(Works_URL)
    works_response = works_request.json()
    works_key = works_response['works'][0]['key'] if 'works' in works_response else None
    if works_request.status_code == 200 and works_key:
        summary_URL = f"http://openlibrary.org/{works_key}.json"
        summary_request = requests.get(summary_URL)
        summary_response = summary_request.json()
        description_data = summary_response['description'] if 'description' in summary_response else None
        if isinstance(description_data, dict) and "value" in description_data:
            summary = description_data["value"]
        else:
            summary = description_data
        
    else:
        summary = 'request for works key failed or works key not available'

    if response.status_code == 200:
        book_data = response.json()
        author = book_data[f'ISBN:{isbn}']['authors'][0]['name']
        title = book_data[f'ISBN:{isbn}']['title']
        cover_url = book_data[f'ISBN:{isbn}']['cover']['medium']

        return {"author": author, "title": title, "summary": summary, "cover_url": cover_url}

    raise HTTPException(status_code=response.status_code, detail="Book details not found")


@app.post("/books/",response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(isbn:str, db: Session = Depends(get_db)):
    "store the book in the library database"
    book_details = get_book_details(isbn)
    title = book_details['title']
    query = crud.get_books_by_title(db, title=title)
    if query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book with this title already exists in the database",
        )
    else:
        return crud.create_book(db=db, book=Book(**book_details))
    

@app.get("/books/", response_model=List[schemas.Book])
def get_all_books(db: Session = Depends(get_db)):
    "return all the stored books in the library database"
    return crud.get_all_books(db)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

