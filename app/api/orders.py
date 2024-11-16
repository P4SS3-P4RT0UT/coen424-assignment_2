import requests
from fastapi import FastAPI, HTTPException
from bson import ObjectId
from data_models.models import Order, DeliveryAddress, OrdersUpdateDeliveryAddressRequest, OrdersUpdateEmailRequest
from mongodb import mongo_client

# events_service = os.getenv("EVENTS_SERVICE")
# event_consume_url = f"http://{events_service}/consume-message"
event_consume_url = "http://events-service:8083/consume-message"
app = FastAPI()
order_db = mongo_client.order
orders_coll = order_db.orders

@app.post("/api/v1/create-order", response_model=Order)
def insert_order(order: Order):
    requests.get(event_consume_url)
    result = orders_coll.insert_one(order.model_dump())
    inserted_order = orders_coll.find_one({"_id": result.inserted_id})
    return inserted_order

@app.put("/api/v1/update-delivery-address", response_model=Order)
def update_delivery_address(request: OrdersUpdateDeliveryAddressRequest):
    requests.get(event_consume_url)
    return update_orders_field(request.order_id, "delivery_address", request.delivery_address.dict())

@app.put("/api/v1/update-user-email", response_model=Order)
def update_user_email(request: OrdersUpdateEmailRequest):
    requests.get(event_consume_url)
    return update_orders_field(request.order_id, "user_email", request.user_email)


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
