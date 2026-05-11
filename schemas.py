from datetime import datetime
from pydantic import BaseModel, model_validator
from models import CarStatus, ContactPreference


class CarCreate(BaseModel):
    reg_number: str
    mileage: int
    mileage_approximate: bool = False
    make: str | None = None
    model: str | None = None
    year: int | None = None
    description: str = ""
    antal_nycklar: int | None = None
    vinterdack: bool = False
    sommardack: bool = False
    dragkrok: bool = False
    servicebehov: bool = False
    extra_info: str = ""
    owner_name: str
    owner_email: str | None = None
    owner_phone: str | None = None
    contact_preference: ContactPreference

    @model_validator(mode="after")
    def check_contact_info(self):
        if self.contact_preference == ContactPreference.email and not self.owner_email:
            raise ValueError("E-postadress krävs när kontaktmetod är email")
        if self.contact_preference == ContactPreference.sms and not self.owner_phone:
            raise ValueError("Telefonnummer krävs när kontaktmetod är sms")
        return self


class CarOut(BaseModel):
    id: int
    reg_number: str
    mileage: int
    mileage_approximate: bool
    make: str | None
    model: str | None
    year: int | None
    description: str
    antal_nycklar: int | None
    vinterdack: bool
    sommardack: bool
    dragkrok: bool
    servicebehov: bool
    extra_info: str
    owner_name: str
    owner_email: str | None
    owner_phone: str | None
    contact_preference: ContactPreference
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
