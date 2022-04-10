import sqlalchemy
from sqlalchemy_utils import database_exists, create_database
from pydantic import BaseModel
from pydantic import BaseSettings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime


class Settings(BaseSettings):
    db_user : str
    db_password : str
    db_host : str
    db_port : int
    db_name : str


settings = Settings()

DATABASE_URL = f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    echo=True,

)

if not database_exists(engine.url):
    create_database(engine.url)
    print("Database created")
else:
    print("Database exists")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TransactionIn(BaseModel):
    amount: float
    currency: str
    description: str
    category: str
    user_id: str
    type: str

    class Config:
        orm_mode = True


class Transaction(Base):
    __tablename__ = "transactions"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    amount = sqlalchemy.Column(sqlalchemy.Numeric, nullable=False)
    currency = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=False, default=sqlalchemy.func.now())
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class TransactionOut(BaseModel):
    id: int
    amount: float
    currency: str
    timestamp: datetime
    description: str
    category: str
    user_id: str
    type: str

    class Config:
        orm_mode = True

Base.metadata.create_all(bind=engine)


def create_transaction(db: Session, transaction: TransactionIn):
    db_tran = Transaction(amount = transaction.amount,
                          currency = transaction.currency,
                          description = transaction.description,
                          category = transaction.category,
                          user_id = transaction.user_id,
                          type = transaction.type)
    db.add(db_tran)
    db.commit()
    db.refresh(db_tran)
    return db_tran


def get_transaction(db: Session, transaction_id: int):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    return transaction


def get_transactions_for_user(db: Session, user_id: str):
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return transactions


def get_transactions_for_user_by_type(db: Session, user_id: str, type: str):
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.type == type).all()
    return transactions


def get_transactions_by_amount(db:Session, amount: float, currency: str, user_id: str):
    transaction = db.query(Transaction).filter(Transaction.amount >= amount,
                                               Transaction.amount <= amount,
                                               Transaction.currency == currency,
                                               Transaction.user_id == user_id).all()
    return transaction


def get_transactions_by_currency(db:Session, currency: str, user_id: str):
    transaction = db.query(Transaction).filter(Transaction.currency == currency,
                                               Transaction.user_id == user_id).all()
    return transaction


def get_transactions_by_amount_range(db:Session, amount_min: float, amount_max: float, currency: str, user_id: str):
    transaction = db.query(Transaction).filter(Transaction.amount >= amount_min,
                                               Transaction.amount <= amount_max,
                                               Transaction.currency == currency,
                                               Transaction.user_id == user_id).all()
    return transaction

def get_transactions_by_category(db:Session, category: str, user_id: str):
    transaction = db.query(Transaction).filter(Transaction.category == category,
                                               Transaction.user_id == user_id).all()
    return transaction


def get_transactions_by_date_range(db:Session, start_date: datetime, end_date: datetime, user_id: str):
    transaction = db.query(Transaction).filter(Transaction.timestamp >= start_date,
                                               Transaction.timestamp <= end_date,
                                               Transaction.user_id == user_id).all()
    return transaction