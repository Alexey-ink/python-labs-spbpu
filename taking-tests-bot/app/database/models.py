from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, String, Integer, ForeignKey, Table
from typing import List

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)

class Test(Base):
    __tablename__ = 'tests'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="tests")
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="test", cascade="all, delete")

class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_text: Mapped[str] = mapped_column(String(255), nullable=False)
    correct_option: Mapped[int] = mapped_column(Integer, nullable=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))

    test: Mapped["Test"] = relationship("Test", back_populates="questions")

class Option(Base):
    __tablename__ = 'options'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    option_text: Mapped[str] = mapped_column(String(255), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))

    question: Mapped["Question"] = relationship("Question", back_populates="options")

Question.options: Mapped[List["Option"]] = relationship("Option", back_populates="question", cascade="all, delete")

class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Связь с тестами: одна категория может иметь много тестов
    tests: Mapped[List["Test"]] = relationship("Test", back_populates="category")

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)