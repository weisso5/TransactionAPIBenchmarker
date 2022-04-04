from typing import Optional
import time
import uuid

from fastapi import Cookie, FastAPI, Request, Response

from functions import fib

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
async def root(response: Response):
    id = str(uuid.uuid4())
    response.set_cookie(key="X-User-Id", value= id)
    return {"message": "Session Started", "userid": id}


@app.get("/calculate/{upto}")
async def say_hello(upto: int, userid: str):
    start_time = time.time()
    rst = [fib(i) for i in range(1, upto)]
    process_time = time.time() - start_time
    return {"totalTime":process_time,
            "upto": upto,
            "userid": userid,
            "results": rst}
