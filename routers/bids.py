from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Bid, Car, CarStatus, Dealer
from schemas import BidCreate, BidOut
from auth import get_current_dealer

router = APIRouter(prefix="/cars", tags=["bids"])


@router.post("/{car_id}/bids", response_model=BidOut, status_code=201)
def create_bid(
    car_id: int,
    bid: BidCreate,
    db: Session = Depends(get_db),
    dealer: Dealer = Depends(get_current_dealer),
):
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Bilen hittades inte")
    if car.status != CarStatus.active:
        raise HTTPException(status_code=400, detail="Det går bara att lägga bud på aktiva bilar")

    db_bid = Bid(car_id=car_id, dealer_id=dealer.id, amount=bid.amount)
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)
    return db_bid


@router.get("/{car_id}/bids", response_model=list[BidOut])
def list_bids(car_id: int, db: Session = Depends(get_db)):
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Bilen hittades inte")
    return car.bids