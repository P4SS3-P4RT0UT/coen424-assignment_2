from fastapi import FastAPI
from api import orders, users

app = FastAPI()

#app.include_router(users.router)
#app.include_router(orders.router)

@app.get("/")
async def root():
    return {"message": "Hello Microservices!"}