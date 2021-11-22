from fastapi.testclient import TestClient
from fastapi import Form, status
import json
from main import app

client = TestClient(app)

def test_encrypt_no_params_no_data():
    response = client.post("/api/encrypt")
    print(response.json())
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_encrypt_param_no_data():
    response = client.post("/api/encrypt?storeType=persistent")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_encrypt_invalid_param_no_data():
    response = client.post("/api/encrypt?storeType=unsupported")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_encrypt_decrypt_volatile():
    secret:str = "password"
    response = client.post("/api/encrypt?storeType=volatile",
                            headers= {"accept": "*/*",
                                    "Content-Type": "application/x-www-form-urlencoded"},
                            data="data="+secret
                            )
    assert response.status_code == 201
    key = json.loads(response.text)['key']
    response = client.get("/api/decrypt?keyName="+key)
    assert response.status_code == 200
    encryptedData = json.loads(response.text)['data']
    assert secret == encryptedData

def test_encrypt_decrypt_persistent():
    secret:str = "password"
    response = client.post("/api/encrypt?storeType=persistent",
                            headers= {"accept": "*/*",
                                    "Content-Type": "application/x-www-form-urlencoded"},
                            data="data="+secret
                            )
    assert response.status_code == 201
    key = json.loads(response.text)['key']
    response = client.get("/api/decrypt?keyName="+key)
    assert response.status_code == 200
    encryptedData = json.loads(response.text)['data']
    assert secret == encryptedData


def test_encrypt_twice():
    secret:str = "password"
    response = client.post("/api/encrypt?storeType=volatile",
                            headers= {"accept": "*/*",
                                    "Content-Type": "application/x-www-form-urlencoded"},
                            data="data="+secret
                            )
    assert response.status_code == 201
    key1= json.loads(response.text)['key']
    response = client.post("/api/encrypt?storeType=volatile",
                            headers= {"accept": "*/*",
                                    "Content-Type": "application/x-www-form-urlencoded"},
                            data="data="+secret
                            )
    key2= json.loads(response.text)['key']
    assert response.status_code == 201
    assert key1 != key2

    response = client.get("/api/decrypt?keyName="+key1)
    val1 = json.loads(response.text)['data']

    response = client.get("/api/decrypt?keyName="+key2)
    val2 = json.loads(response.text)['data']
    assert val1 == val2 == secret


