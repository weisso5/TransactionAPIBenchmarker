from pathlib import Path
from typing import Optional, Dict, List
import time
import uuid
from fastapi import FastAPI, Response, Header, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.backend import TransactionIn, DATABASE_URL, SessionLocal, create_transaction, get_transaction, \
    TransactionOut, get_transactions_for_user, get_transactions_for_user_by_type, get_transactions_by_amount
from app.functions import fib


class CalculateRequest(BaseModel):
    upto: int
    userId: str

class TransactionQuery:
    key: str
    params: Dict[str, object]


app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    print("Starting up")
    print(DATABASE_URL)
    #await database.connect()


@app.on_event("shutdown")
async def shutdown():
    print("Shutting down")
    #await database.disconnect()


@app.get("/", description="Generates a login token")
async def login(response: Response):
    generated = str(uuid.uuid4())
    response.set_cookie(key="X-User-Id", value=generated)
    return {"message": "Generated userId", "userid": generated}


@app.post("/calculate/", description="Calculate fibonacci", summary="Calculate fibonacci to test performance")
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

@app.get("/app/", summary="Get the app", description="returns an html page")
async def app_root():
    p = Path("/code/app/templates/transactionCreator.html")
    template = open(p.absolute(), "r").read()
    return HTMLResponse(template)

@app.post("/transaction/", status_code=status.HTTP_201_CREATED,
          summary="Create a new transaction",
          description="Create a new transaction with amount, currency, user_id, type, description, and category")
async def create(transaction: TransactionIn, db: Session = Depends(get_db)):

    rst = create_transaction(db, transaction)

    return {"id": rst.id, "userId": rst.user_id, "amount": rst.amount, "timestamp": rst.timestamp}


@app.get("/transaction/query/id/{id}", response_model=TransactionOut, summary="Query transaction by id")
async def query_id(id: int, db: Session = Depends(get_db)):
    rst = get_transaction(db, id)
    if rst is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return rst


@app.get("/transaction/query/userId/{userId}", response_model=List[TransactionOut], summary="Query transaction by userId and optionally type")
async def query_userId(userId: str, type: Optional[str] = None, db: Session = Depends(get_db)):
    if type is None:
        rst = get_transactions_for_user(db, userId)
    else:
        rst = get_transactions_for_user_by_type(db, userId, type)
    return rst


@app.get("/transaction/query/userId/{userId}/amount/{amount}/currency/{currency}",
         response_model=List[TransactionOut], summary="Query transaction by userId and amount and currency")
async def query_userId_amount(userId: str, amount: float, currency: str, db: Session = Depends(get_db)):
    rst = get_transactions_by_amount(db, amount, currency, userId)
    return rst


class WebSocketConnectionManager:
    def __init__(self):
        self.clients : List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.clients.remove(websocket)

manager = WebSocketConnectionManager()

async def ws_get_userid(websocket: WebSocket,userid : Optional[str] = Query(None)):
    if userid is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return userid

@app.websocket("/ws/transaction/create")
async def websocket_endpoint(websocket: WebSocket,userid: str = Depends(ws_get_userid), db: Session = Depends(get_db)):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            print(data)
            transaction = TransactionIn(user_id=userid, amount=data["amount"], currency=data["currency"],
                                        type=data["type"], description=data["description"], category=data["category"])
            rst = create_transaction(db, transaction)
            await websocket.send_json(rst)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)