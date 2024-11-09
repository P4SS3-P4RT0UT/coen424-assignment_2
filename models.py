from pydantic import BaseModel, field_validator
from bson.objectid import ObjectId
from typing import Optional

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

    @field_validator('_id', pre=True, always=True)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v