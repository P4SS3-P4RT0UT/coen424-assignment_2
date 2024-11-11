from pydantic import BaseModel, field_validator
from bson.objectid import ObjectId
from typing import Optional, List
from enum import Enum

class DeliveryAddress(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str

class User(BaseModel):
    _id: Optional[str]
    email: str
    first_name: str
    last_name: str
    date_of_birth: str
    phone_number: str
    delivery_address: DeliveryAddress

    @field_validator('_id', check_fields=False)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

class UsersUpdateDeliveryAddressRequest(BaseModel):
    user_id: str
    delivery_address: DeliveryAddress

class UsersUpdateEmailRequest(BaseModel):
    user_id: str
    email: str

class Items(BaseModel):
    item_id: str
    name: str
    quantity: int
    price: float

class OrderStatus(str, Enum):
    under_process = "under process"
    shipping = "shipping"
    delivered = "delivered"

class Order(BaseModel):
    _id: Optional[str]
    user_email: str
    delivery_address: DeliveryAddress
    items: List[Items]
    order_status: OrderStatus
    total_amount: float

    @field_validator('_id', check_fields=False)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v


class OrdersUpdateDeliveryAddressRequest(BaseModel):
    order_id: str
    delivery_address: DeliveryAddress


class OrdersUpdateEmailRequest(BaseModel):
    order_id: str
    user_email: str