import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import Car, CarImage

UPLOAD_DIR = Path("uploads")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

router = APIRouter(prefix="/cars", tags=["images"])


class ImageOut(BaseModel):
    id: int
    url: str

    model_config = {"from_attributes": True}


@router.post("/{car_id}/images", response_model=list[ImageOut], status_code=201)
async def upload_images(
    car_id: int,
    files: Annotated[list[UploadFile], File()],
    db: Session = Depends(get_db),
):
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Bilen hittades inte")

    save_dir = UPLOAD_DIR / str(car_id)
    save_dir.mkdir(parents=True, exist_ok=True)

    saved: list[CarImage] = []
    for file in files:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename}: endast jpg, png och webp är tillåtna",
            )

        data = await file.read()
        if len(data) > MAX_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename}: max 10 MB per bild",
            )

        suffix = Path(file.filename).suffix.lower()
        filename = f"{uuid.uuid4().hex}{suffix}"
        (save_dir / filename).write_bytes(data)

        db_image = CarImage(car_id=car_id, filename=f"{car_id}/{filename}")
        db.add(db_image)
        saved.append(db_image)

    db.commit()
    for img in saved:
        db.refresh(img)

    return [ImageOut(id=img.id, url=f"/static/{img.filename}") for img in saved]


@router.get("/{car_id}/images", response_model=list[ImageOut])
def list_images(car_id: int, db: Session = Depends(get_db)):
    car = db.get(Car, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Bilen hittades inte")
    return [ImageOut(id=img.id, url=f"/static/{img.filename}") for img in car.images]