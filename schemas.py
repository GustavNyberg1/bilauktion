from datetime import datetime
from pydantic import BaseModel, EmailStr
from models import CarStatus


class CarCreate(BaseModel):
    reg_number: str
    make: str
    model: str
    year: int
    mileage: int
    description: str = ""
    antal_nycklar: int = 1
    vinterdack: bool = False
    sommardack: bool = False
    dragkrok: bool = False
    servicebehov: bool = False
    extra_info: str = ""
    owner_name: str
    owner_email: EmailStr
    owner_phone: str


class CarOut(BaseModel):
    id: int
    reg_number: str
    make: str
    model: str
    year: int
    mileage: int
    description: str
    antal_nycklar: int
    vinterdack: bool
    sommardack: bool
    dragkrok: bool
    servicebehov: bool
    extra_info: str
    owner_name: str
    owner_email: str
    owner_phone: str
    status: CarStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class CarCreatedOut(CarOut):
    owner_token: str


class BidCreate(BaseModel):
    amount: float


class BidOut(BaseModel):
    id: int
    car_id: int
    dealer_id: int
    amount: float
    created_at: datetime

    model_config = {"from_attributes": True}
