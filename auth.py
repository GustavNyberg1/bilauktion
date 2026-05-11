from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import Dealer

SECRET_KEY = "byt-ut-denna-i-produktion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(dealer_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(dealer_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_dealer(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Dealer:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ogiltigt eller utgånget token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        dealer_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise credentials_error

    dealer = db.get(Dealer, dealer_id)
    if not dealer:
        raise credentials_error
    return dealer