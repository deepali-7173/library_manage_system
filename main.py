from fastapi import FastAPI, Depends, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from models import Base, User, Book, Student, BorrowDetail
from database import engine, SessionLocal, Base
from datetime import date
from auth import get_password_hash, verify_password, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    username: str
    password: str

# class UserLogin(BaseModel):
#     username: str
#     password: str

@app.post("/register/")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw, role="student")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/token/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

def student_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can borrow books"
        )
    return current_user

def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all borrow records"
        )
    return current_user


class BookRequest(BaseModel):
    book_name: str 
    author_name: str 
    total_quantity: int 
    

@app.get('/')
def index():
    return {"message": "hello"}

@app.post("/books/", tags=["Books"])
async def create_book(book_request:BookRequest, db: Session = Depends(get_db),current_user: User = Depends(admin_required)):
    new_book = Book(**book_request.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"message": "Book added successfully", "book_id": new_book.id}

@app.get("/books/", tags=["Books"])
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books

@app.get("/books/{book_name}", tags=["Books"])
def get_book(book_name: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_name == book_name).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

class StudentRequest(BaseModel):
    Roll_no: int
    student_name: str


@app.post("/students/", tags=["Students"])
async def create_student(student_request:StudentRequest, db: Session = Depends(get_db),current_user: User = Depends(admin_required)):
    new_student = Student(**student_request.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"message": "Student added successfully", "student_id": new_student.id}

@app.get("/students/",tags=["Students"])
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return students

@app.get("/students/{Roll_no}",tags=["Students"])
def get_student(Roll_no: int, db: Session= Depends(get_db)):
    student = db.query(Student).filter(Student.Roll_no ==Roll_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

class BorrowRequest(BaseModel):
    borrow_date: date
    student_id: int
    book_id: int
    #return_date: Optional[date] = Field(default=None, exclude=True)

@app.get("/borrow_details/",tags=["Borrow"])
def get_borrow(db: Session = Depends(get_db)):
    borrow_details = db.query(BorrowDetail).all()
    return borrow_details

@app.post("/borrow_details/",tags=["Borrow"])
async def create_borrow(borrow_request: BorrowRequest, db: Session = Depends(get_db),current_user: User = Depends(student_required)):
    
    book = db.query(Book).filter(Book.id == borrow_request.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.total_quantity <= 0:
        raise HTTPException(status_code=400, detail="Book is out of stock")
    book.total_quantity -= 1    
    new_borrow = BorrowDetail(
        borrow_date=borrow_request.borrow_date,
        return_date=None,
        student_id=borrow_request.student_id,
        book_id=borrow_request.book_id
    )
    db.add(new_borrow)
    db.commit()
    db.refresh(new_borrow)

    return {
        "message": "Borrow details added successfully",
        "borrow_id": new_borrow.id,
        "remaining_quantity": book.total_quantity
    }

@app.put ("/borrow_details{borrow_id}/return", tags=["Borrow"])
async def return_book(borrow_id=int, db:Session = Depends(get_db),current_user: User = Depends(student_required)):
    borrow=db.query(BorrowDetail).filter(BorrowDetail.id==borrow_id).first()
    if not borrow:
        raise HTTPException(status_code=404, detail="Borrow record not found")
    if borrow.return_date is not None:
        raise HTTPException(status_code=400, detail="Book already returned")
    borrow.return_date = date.today()
    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    if book:
        book.total_quantity += 1
    db.commit()
    db.refresh(borrow)    
    return {
        "message": "Book returned successfully",
        "borrow_id": borrow.id,
        "return_date": borrow.return_date,
        "updated_stock": book.total_quantity if book else None
    }

