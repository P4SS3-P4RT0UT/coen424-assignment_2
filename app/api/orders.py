import os
import json

import httpx
from fastapi import FastAPI, HTTPException, Request
import requests
from bson import ObjectId
from data_models.models import Order, DeliveryAddress, OrdersUpdateDeliveryAddressRequest, OrdersUpdateEmailRequest, OrderStatus, OrdersUpdateStatusRequest
from mongodb import mongo_client
from typing import Union

events_service = os.getenv("EVENTS_SERVICE")
event_consume_url = f"{events_service}/message"
# event_consume_url = "http://events-service:8083/message"

app = FastAPI()
order_db = mongo_client.order
orders_coll = order_db.orders


@app.middleware("http")
async def add_event_consume_url(request: Request, call_next):
    try:
        # Asynchronous call to the event consumer URL
        async with httpx.AsyncClient() as client:
            response = await client.get(event_consume_url)
            if response.status_code != 200:
                print(f"Warning: Event consumer returned status {response.status_code}")
    except Exception as e:
        print(f"Error calling event consumer: {e}")

    # Proceed with the main request
    return await call_next(request)
@app.post("/api/v1/orders", response_model=Order)
def insert_order(order: Order):
    result = orders_coll.insert_one(order.model_dump())
    inserted_order = orders_coll.find_one({"_id": result.inserted_id})
    return inserted_order

@app.put("/api/v1/orders", response_model=Order)
def update_order_field(request: Union[OrdersUpdateDeliveryAddressRequest, OrdersUpdateEmailRequest]):
    if isinstance(request, OrdersUpdateDeliveryAddressRequest):
        return update_orders_field(request.order_id, "delivery_address", request.delivery_address.dict())
    elif isinstance(request, OrdersUpdateEmailRequest):
        return update_orders_field(request.order_id, "user_email", request.user_email)
    else:
        raise HTTPException(status_code=400, detail="Invalid request type")


def update_orders_field(order_id, field, value):
    try:
        order_id = ObjectId(order_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order_id format")
    result = orders_coll.update_one({"_id": order_id}, {"$set": {field: value}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    updated_order = orders_coll.find_one({"_id": order_id})
    if updated_order:
        updated_order["_id"] = str(updated_order["_id"])
        updated_order["user_id"] = str(updated_order["user_id"])
        return updated_order
    else:
        raise HTTPException(status_code=404, detail="Order not found after update")

@app.put("/api/v1/orders/status", response_model=Order)
def update_order_status(request: OrdersUpdateStatusRequest):
    return update_orders_field(request.order_id, "order_status", request.order_status)

@app.get("/api/v1/orders/status/{order_status}/all")
def get_orders_with_status(order_status: OrderStatus):
    cursor = orders_coll.find({"order_status": order_status})
    orders = []
    for doc in cursor:
        doc = json.loads(json.dumps(doc, default=str))
        orders.append(doc)
    return {"orders": orders}