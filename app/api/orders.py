from fastapi import FastAPI
from data_models.models import Order
from mongodb import mongo_client

app = FastAPI()

@app.post("/api/v1/create-order", response_model=Order)
def insert_order(order: Order):
    order_db = mongo_client.order
    orders_coll = order_db.orders
    result = orders_coll.insert_one(order.model_dump())
    inserted_order = orders_coll.find_one({"_id": result.inserted_id})
    return inserted_order