import requests


def test_python_ok():
    assert 1 + 1 == 2


def test_requests_ok():
    r = requests.get("https://httpbin.org/get", timeout=10)
    assert r.status_code == 200
    assert r.json()["url"].endswith("/get")