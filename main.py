import databases, sqlalchemy, uuid
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

# Database
DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
db = sqlalchemy

books = sqlalchemy.Table(
    "books",
    metadata,
    db.Column("id", db.String, primary_key=True),
    db.Column("external_id", db.String),
    db.Column("title", db.String),
    db.Column("authors", db.String),
    db.Column("published_year", db.Integer),
    db.Column("aquired", db.Boolean),
    db.Column("thumbnail", db.String)
)

engine = db.create_engine(DATABASE_URL)
metadata.create_all(engine)

# MODELS


class BookList(BaseModel):
    id: str
    external_id: str
    title: str
    authors: str
    published_year: int
    aquired: bool
    thumbnail: str


class BookEntry(BaseModel):
    external_id: str = Field(..., example="XYZ")
    title: str = Field(..., example="Quo Vadis")
    authors: str = Field(..., example="H.Sienkiewicz")
    published_year: int = Field(..., example="1896")
    aquired: bool = Field(..., example="true")
    thumbnail: str = Field(..., example="http...")


class BookUpdate(BaseModel):
    id: str = Field(..., example="enter your ID")
    external_id: str = Field(..., example="XYZ")
    title: str = Field(..., example="Quo Vadis")
    authors: str = Field(..., example="H.Sienkiewicz")
    published_year: int = Field(..., example="1896")
    aquired: bool = Field(..., example="true")
    thumbnail: str = Field(..., example="http...")


class BookDelete(BaseModel):
    id: str = Field(..., example="enter your ID")


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def home():
    return "Hello Mr.Czesław!"

@app.get("/books", response_model=List[BookList])
async def get_all_books():
    query = books.select()
    return await database.fetch_all(query)

@app.get("/books/{book_id}", response_model=BookList)
async def find_book_by_id(book_id: str):
    query = books.select().where(books.c.id == book_id)
    return await database.fetch_one(query)

@app.get("/books/year/{year_range}", response_model=List[BookList])
async def get_all_books_from_year_range(year_from: int, year_to: int):
    query = books.select().\
        where(books.c.published_year >= year_from).where(books.c.published_year <= year_to)
    return await database.fetch_all(query)

@app.get("/books/title/{title}", response_model=List[BookList])
async def get_all_books_by_title(title: str):
    query = books.select().\
        where(books.c.title.like('%' + title + '%'))
    return await database.fetch_all(query)

@app.get("/books/author/{author}", response_model=List[BookList])
async def get_all_books_by_author(author: str):
    query = books.select().\
        where(books.c.title.like('%' + author + '%'))
    return await database.fetch_all(query)

@app.get("/books/aquired/{aquired}", response_model=List[BookList])
async def get_all_books_by_aquired_state(aquired: bool):
    query = books.select().\
        where(books.c.aquired == aquired)
    return await database.fetch_all(query)

@app.post("/books", response_model=BookList)
async def add_book(book: BookEntry):
    gID = str(uuid.uuid1())
    query = books.insert().values(
        id=gID,
        external_id=book.external_id,
        title=book.title,
        authors=book.authors,
        published_year=book.published_year,
        aquired=book.aquired,
        thumbnail=book.thumbnail,
    )
    await database.execute(query)
    return {"id": str(gID), **book.dict()}

@app.put("/books", response_model=BookList)
async def update_book(book: BookUpdate):
    query = books.update().where(books.c.id == book.id).values(
        external_id=book.external_id,
        title=book.title,
        authors=book.authors,
        published_year=book.published_year,
        aquired=book.aquired,
        thumbnail=book.thumbnail
    )

    await database.execute(query)
    return await find_book_by_id(book.id)

@app.delete("/books/{book_id}")
async def delete_book(book:BookDelete):
    query = books.delete().where(books.c.id == book_id)
    await database.execute(query)

    return {
        "status" : True,
        "message": "Book has been deleted."
    }

