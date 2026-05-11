import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Car, CarStatus, Bid
from schemas import CarCreate, CarOut, CarCreatedOut, BidOut

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("/", response_model=CarCreatedOut, status_code=201)
def create_car(car: CarCreate, db: Session = Depends(get_db)):
    db_car = Car(**car.model_dump(), owner_token=secrets.token_urlsafe(32))
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


@router.get("/", response_model=list[CarOut])
def list_cars(db: Session = Depends(get_db)):
    return db.query(Car).filter(Car.status == CarStatus.active).all()


@router.get("/{car_id}", response_model=CarOut)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Bilen hittades inte")
    return car


@router.post("/{car_id}/bids/{bid_id}/accept", response_model=BidOut)
def accept_bid(car_id: int, bid_id: int, owner_token: str, db: Session = Depends(get_db)):
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Bilen hittades inte")
    if car.owner_token != owner_token:
        raise HTTPException(status_code=403, detail="Ogiltig ägarnyckel")
    if car.status != CarStatus.active:
        raise HTTPException(status_code=400, detail="Bilen är inte aktiv")

    bid = db.get(Bid, bid_id)
    if not bid or bid.car_id != car_id:
        raise HTTPException(status_code=404, detail="Budet hittades inte")

    car.status = CarStatus.sold
    db.commit()
    db.refresh(bid)
    return bid
