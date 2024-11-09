from fastapi import FastAPI
from mongodb import mongo_client
from models import User, Order

app = FastAPI()

@app.get("/")
def root():
    return {"Welcome": "!"}

@app.get("/api/v1/read-all-users")
def get_users():
    user_db = mongo_client.user
    users_coll = user_db.users
    cursor = users_coll.find({})
    users = []
    for record in cursor:
        record['_id'] = str(record['_id'])
        users.append(record)
    return {"users": users}

@app.post("/api/v1/create-user", response_model=User)
def insert_user(user: User):
    user_db = mongo_client.user
    users_coll = user_db.users
    result = users_coll.insert_one(user.model_dump())
    inserted_user = users_coll.find_one({"_id": result.inserted_id})
    return inserted_user

@app.post("/api/v1/create-order", response_model=Order)
def insert_order(order: Order):
    order_db = mongo_client.order
    orders_coll = order_db.orders
    result = orders_coll.insert_one(order.model_dump())
    inserted_order = orders_coll.find_one({"_id": result.inserted_id})
    return inserted_order