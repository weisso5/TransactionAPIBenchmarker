from typing import Optional
import time
import uuid
from fastapi import FastAPI, Response, Header, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from app.backend import Transaction, TransactionIn, DATABASE_URL, SessionLocal, createTransaction
from app.functions import fib


class CalculateRequest(BaseModel):
    upto: int
    userId: str


app = FastAPI()
db = SessionLocal()

@app.on_event("startup")
async def startup():
    print("Starting up")
    print(DATABASE_URL)
    #await database.connect()


@app.on_event("shutdown")
async def shutdown():
    print("Shutting down")
    #await database.disconnect()


@app.get("/")
async def root(response: Response):
    generated = str(uuid.uuid4())
    response.set_cookie(key="X-User-Id", value=generated)
    return {"message": "Generated userId", "userid": generated}


@app.post("/calculate/")
async def calculate(item: CalculateRequest,
                    user_agent: Optional[str] = Header(None)):
    start_time = time.process_time()
    rst = [fib(i) for i in range(1, item.upto)]
    process_time = round((time.process_time() - start_time) * 1000, 2)
    return {
            "requestor": user_agent,
            "totalTime": str(process_time) + "ms",
            "upto": item.upto,
            "userid": item.userId,
            "results": rst}


@app.post("/transaction/")
async def create(transaction: TransactionIn):

    rst = createTransaction(db, transaction)

    return {"id": rst.id, "userId": rst.user_id, "amount": rst.amount, "timestamp": rst.timestamp}