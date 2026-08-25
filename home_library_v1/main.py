'''
home_library_v1 / main.py
-----------------------------
1단계 저장(저장 기능 추가) - ISBN 조회 + DB 저장
'''
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session # from sqlalchemy import Session
from database import Base, engine, get_db
from models import Book
from services.recognition import lookup_metadata, normalize_isbn

Base.metadata.create_all(engine)

app = FastAPI(title='우리집 책장 API')

# --------------------------------------------------------------------
# GET    /books/lookup --> ISBN 문자열만으로 책 정보를 바로 조회하는 API
#---------------------------------------------------------------------
@app.get('/books/lookup')
def lookup_book(isbn: str, db: Session = Depends(get_db)):
    validated_isbn = normalize_isbn(isbn)

    if not validated_isbn:
        raise HTTPException(422, '유효한 ISBN 형식이 아닙니다.')
    
    existing_book = db.scalar(select(Book).where(Book.isbn == validated_isbn))
    if existing_book:
        raise HTTPException(
            409,
            f'이미 등록된 책입니다: {existing_book.title} (id={existing_book.id})',
        )

    metadata = lookup_metadata(validated_isbn)

    if not metadata:
        raise HTTPException(404, '조회된 서지정보가 없습니다.')

    book = Book(
        title=metadata['title'],
        isbn=metadata['isbn'],
        author=metadata['author'],
        publisher=metadata['publisher'],
        cover_path=None,
        recognition_status='confirmed',
    )

    # 데이터베이스에 저장
    db.add(book)
    db.commit()
    db.refresh(book)

    return book

# --------------------------------------------------------------------
# GET    /books -->등록된 책 전체 목록을 돌려주는 API
#---------------------------------------------------------------------
@app.get('/books')
def list_books(db: Session = Depends(get_db)):
    return db.scalars(select(Book)).all()


