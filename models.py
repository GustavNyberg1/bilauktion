from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import enum

from database import Base


class CarStatus(str, enum.Enum):
    active = "active"
    sold = "sold"
    expired = "expired"


class ContactPreference(str, enum.Enum):
    email = "email"
    sms = "sms"


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    reg_number = Column(String, unique=True, index=True, nullable=False)
    make = Column(String, nullable=True)
    model = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    mileage = Column(Integer, nullable=False)
    description = Column(String, default="")
    antal_nycklar = Column(Integer, nullable=True)
    vinterdack = Column(Boolean, default=False)
    sommardack = Column(Boolean, default=False)
    dragkrok = Column(Boolean, default=False)
    servicebehov = Column(Boolean, default=False)
    extra_info = Column(String, default="")
    owner_name = Column(String, nullable=False)
    owner_email = Column(String, nullable=True)
    owner_phone = Column(String, nullable=True)
    contact_preference = Column(Enum(ContactPreference), nullable=False)
    owner_token = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(CarStatus), default=CarStatus.active, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bids = relationship("Bid", back_populates="car")
    images = relationship("CarImage", back_populates="car")


class Dealer(Base):
    __tablename__ = "dealers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bids = relationship("Bid", back_populates="dealer")


class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    dealer_id = Column(Integer, ForeignKey("dealers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    car = relationship("Car", back_populates="bids")
    dealer = relationship("Dealer", back_populates="bids")


class CarImage(Base):
    __tablename__ = "car_images"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    car = relationship("Car", back_populates="images")