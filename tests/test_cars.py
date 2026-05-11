CAR_PAYLOAD = {
    "reg_number": "ABC123",
    "mileage": 8000,
    "make": "Volvo",
    "model": "V70",
    "year": 2018,
    "owner_name": "Anna Svensson",
    "owner_email": "anna@test.se",
    "contact_preference": "email",
    "antal_nycklar": 2,
    "vinterdack": True,
    "dragkrok": True,
    "extra_info": "Välvårdad bil",
}

MINIMAL_PAYLOAD = {
    "reg_number": "XYZ999",
    "mileage": 5000,
    "owner_name": "Bo",
    "owner_phone": "070-1234567",
    "contact_preference": "sms",
}


def test_create_car_returns_owner_token(client):
    resp = client.post("/cars/", json=CAR_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert "owner_token" in data
    assert len(data["owner_token"]) > 20
    assert data["dragkrok"] is True
    assert data["antal_nycklar"] == 2


def test_create_car_minimal_fields(client):
    resp = client.post("/cars/", json=MINIMAL_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["make"] is None
    assert data["year"] is None
    assert data["contact_preference"] == "sms"


def test_contact_email_requires_email(client):
    resp = client.post("/cars/", json={
        "reg_number": "ERR001", "mileage": 1000,
        "owner_name": "X", "contact_preference": "email",
    })
    assert resp.status_code == 422


def test_contact_sms_requires_phone(client):
    resp = client.post("/cars/", json={
        "reg_number": "ERR002", "mileage": 1000,
        "owner_name": "X", "contact_preference": "sms",
    })
    assert resp.status_code == 422


def test_list_only_active_cars(client):
    client.post("/cars/", json=CAR_PAYLOAD)
    resp = client.get("/cars/")
    assert resp.status_code == 200
    cars = resp.json()
    assert len(cars) == 1
    assert "owner_token" not in cars[0]


def test_accept_bid_marks_car_as_sold(client, auth_headers):
    car_resp = client.post("/cars/", json=CAR_PAYLOAD)
    car = car_resp.json()
    car_id = car["id"]
    owner_token = car["owner_token"]

    bid_resp = client.post(f"/cars/{car_id}/bids", json={"amount": 90000}, headers=auth_headers)
    bid_id = bid_resp.json()["id"]

    accept_resp = client.post(
        f"/cars/{car_id}/bids/{bid_id}/accept",
        params={"owner_token": owner_token},
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["id"] == bid_id

    car_after = client.get(f"/cars/{car_id}").json()
    assert car_after["status"] == "sold"


def test_accept_bid_wrong_token(client, auth_headers):
    car_resp = client.post("/cars/", json=CAR_PAYLOAD)
    car_id = car_resp.json()["id"]
    bid_resp = client.post(f"/cars/{car_id}/bids", json={"amount": 50000}, headers=auth_headers)
    bid_id = bid_resp.json()["id"]

    resp = client.post(
        f"/cars/{car_id}/bids/{bid_id}/accept",
        params={"owner_token": "fel-token"},
    )
    assert resp.status_code == 403


def test_sold_car_not_in_list(client, auth_headers):
    car_resp = client.post("/cars/", json=CAR_PAYLOAD)
    car = car_resp.json()
    car_id = car["id"]
    owner_token = car["owner_token"]

    bid_resp = client.post(f"/cars/{car_id}/bids", json={"amount": 60000}, headers=auth_headers)
    bid_id = bid_resp.json()["id"]
    client.post(f"/cars/{car_id}/bids/{bid_id}/accept", params={"owner_token": owner_token})

    resp = client.get("/cars/")
    assert resp.json() == []
