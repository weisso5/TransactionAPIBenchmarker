import sqlalchemy
from sqlalchemy_utils import database_exists, create_database
from pydantic import BaseModel
from pydantic import BaseSettings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime

from faker import Faker
from faker.providers import bank, currency, internet, profile, company, job, date_time


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

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    amount = sqlalchemy.Column(sqlalchemy.Numeric, nullable=False)
    currency = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=False, default=sqlalchemy.func.now())
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.id"), nullable=False, index=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    user = relationship("User", back_populates="transactions")


class TransactionOut(BaseModel):
    id: int
    amount: float
    currency: str
    timestamp: datetime
    description: str
    category: str
    user_id: str
    type: str
    date : str
    time : str
    timezone : str

    class Config:
        orm_mode = True


class UserIn(BaseModel):

    name: str
    email: str

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    timestamp: datetime

    class Config:
        orm_mode = True


class User(Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=False, default=sqlalchemy.func.now())

    transactions = relationship("Transaction", back_populates="user")


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


def create_transactions_for_user(db: Session, user_id: str, number: int):
    fake = Faker()
    fake.add_provider(bank)
    fake.add_provider(currency)
    fake.add_provider(internet)
    fake.add_provider(profile)
    fake.add_provider(company)
    fake.add_provider(job)
    fake.add_provider(date_time)

    transactions = []

    for x in range(number):
        tran = Transaction(amount = fake.pricetag().replace(",", "")[1:],
                             currency = fake.currency_code(),
                             description = fake.company(),
                             category = fake.job(),
                             user_id = user_id,
                             type = "credit" if x % 2 == 0 else "debit",
                           timestamp=fake.date_time_this_decade())
        db.add(tran)
        db.commit()
        db.refresh(tran)
        transactions.append(add_formatted_date(tran))

    return list(transactions)


def add_formatted_date(tran: Transaction):
    tran.date = tran.timestamp.strftime("%m/%d/%Y")
    tran.time = tran.timestamp.strftime("%H:%M:%S")
    tran.timezone = tran.timestamp.strftime("%Z")
    return tran


def get_transaction(db: Session, transaction_id: int):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    add_formatted_date(transaction)
    return transaction


def get_transactions_for_user(db: Session, user_id: str):
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id)\
        .order_by(Transaction.timestamp.desc()).all()
    mapped = [add_formatted_date(tran) for tran in transactions]
    return mapped


def get_transactions_for_user_by_type(db: Session, user_id: str, type: str):
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.type == type)\
        .order_by(Transaction.timestamp.desc()).all()
    mapped = [add_formatted_date(tran) for tran in transactions]
    return mapped


def get_transactions_by_amount(db:Session, amount: float, currency: str, user_id: str):
    transactions = db.query(Transaction).filter(Transaction.amount >= amount,
                                               Transaction.amount <= amount,
                                               Transaction.currency == currency,
                                               Transaction.user_id == user_id)\
        .order_by(Transaction.timestamp.desc()).all()
    mapped = [add_formatted_date(tran) for tran in transactions]
    return mapped


def get_transactions_by_currency(db:Session, currency: str, user_id: str):
    transactions = db.query(Transaction).filter(Transaction.currency == currency,
                                               Transaction.user_id == user_id)\
        .order_by(Transaction.timestamp.desc()).all()
    mapped = [add_formatted_date(tran) for tran in transactions]
    return mapped


def get_transactions_by_amount_range(db:Session, amount_min: float, amount_max: float, currency: str, user_id: str):
    transactions = db.query(Transaction).filter(Transaction.amount >= amount_min,
                                               Transaction.amount <= amount_max,
                                               Transaction.currency == currency,
                                               Transaction.user_id == user_id)\
        .order_by(Transaction.timestamp.desc()).all()
    mapped = [add_formatted_date(tran) for tran in transactions]
    return mapped


def get_transactions_by_category(db:Session, category: str, user_id: str):
    transactions = db.query(Transaction).filter(Transaction.category == category,
                                               Transaction.user_id == user_id)\
        .order_by(Transaction.timestamp.desc()).all()
    mapped = [add_formatted_date(tran) for tran in transactions]
    return mapped


def get_transactions_by_date_range(db:Session, start_date: datetime, end_date: datetime, user_id: str):
    transactions = db.query(Transaction).filter(Transaction.timestamp >= start_date,
                                               Transaction.timestamp <= end_date,
                                               Transaction.user_id == user_id)\
        .order_by(Transaction.timestamp.desc()).all()
    mapped = [add_formatted_date(tran) for tran in transactions]
    return mapped


def user_exists(db: Session, user_email: str):
    return db.query(User).filter(User.email == user_email).first() is not None


def valid_user(db:Session, user_token: str):
    return db.query(User).filter(User.id == user_token).first() is not None


def get_user(db: Session, user_email: str):
    return db.query(User).filter(User.email == user_email).first()


def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, id: str, u : UserIn):
    db_user = User(id = id,name= u.name, email = u.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user