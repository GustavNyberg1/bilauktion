def test_register_dealer(client):
    resp = client.post("/auth/register", json={
        "company_name": "Bilar AB",
        "email": "ny@dealer.se",
        "password": "lösenord123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "ny@dealer.se"
    assert data["company_name"] == "Bilar AB"
    assert "id" in data


def test_register_duplicate_email(client):
    payload = {"company_name": "A", "email": "dup@test.se", "password": "abc"}
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={
        "company_name": "X", "email": "x@x.se", "password": "pass"
    })
    resp = client.post("/auth/login", data={"username": "x@x.se", "password": "pass"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "company_name": "X", "email": "x@x.se", "password": "rätt"
    })
    resp = client.post("/auth/login", data={"username": "x@x.se", "password": "fel"})
    assert resp.status_code == 401


def test_bid_requires_auth(client):
    car = client.post("/cars/", json={
        "reg_number": "ABC123", "make": "Volvo", "model": "V70",
        "year": 2018, "mileage": 8000, "owner_name": "Anna",
        "owner_email": "anna@test.se", "owner_phone": "070-1234567",
    })
    car_id = car.json()["id"]
    resp = client.post(f"/cars/{car_id}/bids", json={"amount": 50000})
    assert resp.status_code == 401


def test_bid_with_auth(client, auth_headers):
    car = client.post("/cars/", json={
        "reg_number": "DEF456", "make": "Saab", "model": "9-3",
        "year": 2015, "mileage": 12000, "owner_name": "Bo",
        "owner_email": "bo@test.se", "owner_phone": "070-7654321",
    })
    car_id = car.json()["id"]
    resp = client.post(f"/cars/{car_id}/bids", json={"amount": 75000}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["amount"] == 75000
    assert "dealer_id" in data