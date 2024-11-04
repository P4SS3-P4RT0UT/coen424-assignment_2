from fastapi import FastAPI
from mongodb import mongo_client

app = FastAPI()

@app.get("/users")
def root():
    return {"Hello": "World"}