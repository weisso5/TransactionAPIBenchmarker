import sqlalchemy
from pydantic import BaseModel
from pydantic import BaseSettings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


class Settings(BaseSettings):
    db_user : str
    db_password : str
    db_host : str
    db_port : int
    db_name : str


settings = Settings()

DATABASE_URL = f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
#database = databases.Database(DATABASE_URL)

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
#
# metadata = sqlalchemy.MetaData()
#
# transactions = sqlalchemy.Table(
#     "transactions",
#     metadata,
#     sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
#     sqlalchemy.Column("amount", sqlalchemy.Numeric, nullable=False),
#     sqlalchemy.Column("currency", sqlalchemy.String, nullable=False),
#     sqlalchemy.Column("timestamp", sqlalchemy.DateTime(timezone=True), nullable=False, default=sqlalchemy.func.now()),
#     sqlalchemy.Column("description", sqlalchemy.String, nullable=True),
#     sqlalchemy.Column("category", sqlalchemy.String, nullable=False),
#     sqlalchemy.Column("type", sqlalchemy.String, nullable=False),
#     sqlalchemy.Column("user_id", sqlalchemy.String, nullable=False),
# )
#
# metadata.drop_all(engine)
# metadata.create_all(engine)


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

def createTransaction(db: Session, transaction: TransactionIn):
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