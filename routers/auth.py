from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import get_db
from models import Dealer
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class DealerRegister(BaseModel):
    company_name: str
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DealerOut(BaseModel):
    id: int
    company_name: str
    email: str

    model_config = {"from_attributes": True}


@router.post("/register", response_model=DealerOut, status_code=201)
def register(data: DealerRegister, db: Session = Depends(get_db)):
    if db.query(Dealer).filter(Dealer.email == data.email).first():
        raise HTTPException(status_code=400, detail="E-postadressen är redan registrerad")
    dealer = Dealer(
        company_name=data.company_name,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(dealer)
    db.commit()
    db.refresh(dealer)
    return dealer


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    dealer = db.query(Dealer).filter(Dealer.email == form.username).first()
    if not dealer or not verify_password(form.password, dealer.hashed_password):
        raise HTTPException(status_code=401, detail="Fel e-post eller lösenord")
    return TokenOut(access_token=create_access_token(dealer.id))