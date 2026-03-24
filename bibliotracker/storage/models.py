from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    region = Column(String, nullable=True)
    subjects = Column(Text, nullable=True)  # Stored as comma-separated values
    is_fiction = Column(String, nullable=True)  # Store "Fiction" or "Non-Fiction"
    is_owned = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Book(title={self.title}, author={self.author})>"
