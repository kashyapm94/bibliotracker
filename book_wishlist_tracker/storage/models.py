from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    isbn = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    country = Column(String, nullable=True)
    region = Column(String, nullable=True)
    subjects = Column(Text, nullable=True)  # Stored as comma-separated values

    def __repr__(self):
        return f"<Book(title={self.title}, author={self.author})>"
