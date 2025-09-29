from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(255), default="student", nullable=False)
    name = Column(String(50), nullable=True)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    book_name= Column(String(255), nullable= False)
    author_name= Column(String(255), nullable=False)
    total_quantity= Column(Integer, default=1)
    published_year = Column(Integer, nullable=True)
    borrows = relationship("BorrowDetail", back_populates="book")

class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True)
    Roll_no = Column(Integer,unique=True)
    student_name = Column(String(255), nullable=False)
    borrows = relationship("BorrowDetail", back_populates="student")

class BorrowDetail(Base):
    __tablename__="borrow_details"
    id = Column(Integer, primary_key=True)
    borrow_date=Column(Date, nullable=False)
    return_date=Column(Date, nullable=True,)
    student_id = Column(Integer, ForeignKey("student.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    student = relationship("Student", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")
