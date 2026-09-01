'''
home_library_v2 / main.py
-----------------------------
2단계 - 중복 등록 응답을 에러가 아닌 메세지로 개선
        detail을 딕셔너리로 구조화해서, 기존 책의 제목/저자/출판사/상태를 각각 따로 꺼내 사용할 수 있게 한다.
'''
import io
import uuid  # 충돌없는 고유한 이름을 자동으로 만들어주는 라이브러리(식별자)
from pathlib import Path
from fastapi import Depends, FastAPI, File, Form, UploadFile, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError
from database import Base, engine, get_db
from models import Book
from services.recognition import lookup_metadata, normalize_isbn

UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok=True)

Base.metadata.create_all(engine)

app = FastAPI(title='우리집 책장 API')

def _duplicate_detail(existing_book: Book) -> dict:
    """
    중복된 책을 만났을 때 응답에 실을 정보를 한 곳에서 만든다.
    lookup_book, register_book 두 군데에서 똑같이 재사용하기 위한 헬퍼 함수
    """
    return {
        'message': '이미 등록된 책입니다.',
        'existing_book': {
            'id': existing_book.id,
            'title': existing_book.title,
            'author': existing_book.author,
            'publisher': existing_book.publisher,
            'recognition_status': existing_book.recognition_status,
        },
    }

@app.get('/books/lookup')
def lookup_book(isbn: str, db: Session = Depends(get_db)):
    """
    ISBN 문자열만으로 서지정보를 조회하고 DB에 저장    
    """
    validated_isbn = normalize_isbn(isbn)

    if not validated_isbn:
        raise HTTPException(422, '유효한 ISBN 형식이 아닙니다.')

    existing_book = db.scalar(select(Book).where(Book.isbn == validated_isbn)) # 같은 책을 찾는 것

    if existing_book: # 중복된 책이 있다면 409에러 발생 -> _duplicate_detail 헬퍼 함수 호출
        raise HTTPException(status.HTTP_409_CONFLICT, _duplicate_detail(existing_book))

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

    db.add(book)
    db.commit()
    db.refresh(book)

    return book

@app.post('/books/register', status_code=status.HTTP_201_CREATED)
def register_book(isbn: str=Form(...), image: UploadFile=File(...), db: Session=Depends(get_db)):
    """
    ISBN + 표지 사진을 함께 등록
    """
    validated_isbn = normalize_isbn(isbn)
    if not validated_isbn:
        raise HTTPException(422, '유효한 ISBN 형식이 아닙니다.')

    existing_book = db.scalar(select(Book).where(Book.isbn == validated_isbn)) # 중복 확인
    if existing_book:
        raise HTTPException(status.HTTP_409_CONFLICT, _duplicate_detail(existing_book))

    raw = image.file.read()  # 이미지 읽는다.
    try:
        with Image.open(io.BytesIO(raw)) as probe:
            probe.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(415, '올바른 이미지 파일이 아닙니다.')

    # uuid 파일명으로 저장 
    # Path(image.filename).suffix --> 원본 파일의 확장자만 뽑아온다. ex)'.jpg'
    #       확장자가 없는 이상한 파일이 올라올 경우를 대비해 기본값 '.jpg'
    extension = Path(image.filename).suffix or '.jpg'

    # uuid.uuid4() --> 충돌 확률이 사실상 0에 가까운 랜덤 UUID를 생성
    # .hex --> 하이픈(-) 없는 32자리 영문/숫자 문자열로 변환
    # 원본 파일명을 그대로 안쓰고 이 문자열로 교체
    #   1) 같은 이름의 파일이 두 번 업로드되어도 덮어쓰기 걱정이 없다. 데이터 소실 문제 해결
    #   2) 한글 파일명이 환경에 따라 깨지거나 다운로드 실패나는 문제도 방지
    filename = f'{uuid.uuid4().hex}{extension}'

    path = UPLOAD_DIR / filename # pathlib가 OS에 맞는 경로 구분자로 알아서 합쳐준다.

    path.write_bytes(raw) # 앞에서 읽어둔 원본 이미지 바이트를 실제 파일로 저장

    metadata = lookup_metadata(validated_isbn)

    if metadata:
        title = metadata['title']
        author = metadata['author']
        publisher = metadata['publisher']
        status_value = 'confirmed'
    else:
        title = f'수동 등록: ISBN {validated_isbn} (서지정보 조회 실패)'
        author = None
        publisher = None
        status_value = 'needs_review'

    book = Book(
        title=title,
        isbn=validated_isbn,
        author=author,
        publisher=publisher,
        cover_path=str(path),
        recognition_status= status_value,
    )

    db.add(book)
    db.commit()
    db.refresh(book)

    return book

@app.get('/books')
def list_books(db: Session=Depends(get_db)):
    """등록된 책 전체 목록을 돌려주는 API"""
    return db.scalars(select(Book)).all()