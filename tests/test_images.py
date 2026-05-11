import io
from PIL import Image as PILImage
import pytest


def make_image_bytes(fmt="JPEG") -> bytes:
    img = PILImage.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


CAR_PAYLOAD = {
    "reg_number": "IMG001",
    "mileage": 5000,
    "owner_name": "Kalle",
    "owner_email": "kalle@test.se",
    "contact_preference": "email",
}


@pytest.fixture
def car_id(client):
    resp = client.post("/cars/", json=CAR_PAYLOAD)
    return resp.json()["id"]


def test_upload_single_image(client, car_id):
    files = [("files", ("foto.jpg", make_image_bytes(), "image/jpeg"))]
    resp = client.post(f"/cars/{car_id}/images", files=files)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 1
    assert data[0]["url"].startswith("/static/")
    assert data[0]["url"].endswith(".jpg")


def test_upload_multiple_images(client, car_id):
    files = [
        ("files", ("a.jpg", make_image_bytes("JPEG"), "image/jpeg")),
        ("files", ("b.png", make_image_bytes("PNG"), "image/png")),
        ("files", ("c.webp", make_image_bytes("WEBP"), "image/webp")),
    ]
    resp = client.post(f"/cars/{car_id}/images", files=files)
    assert resp.status_code == 201
    assert len(resp.json()) == 3


def test_upload_invalid_filetype(client, car_id):
    files = [("files", ("doc.pdf", b"pdfdata", "application/pdf"))]
    resp = client.post(f"/cars/{car_id}/images", files=files)
    assert resp.status_code == 400


def test_list_images(client, car_id):
    files = [
        ("files", ("x.jpg", make_image_bytes(), "image/jpeg")),
        ("files", ("y.jpg", make_image_bytes(), "image/jpeg")),
    ]
    client.post(f"/cars/{car_id}/images", files=files)
    resp = client.get(f"/cars/{car_id}/images")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_upload_to_nonexistent_car(client):
    files = [("files", ("x.jpg", make_image_bytes(), "image/jpeg"))]
    resp = client.post("/cars/9999/images", files=files)
    assert resp.status_code == 404