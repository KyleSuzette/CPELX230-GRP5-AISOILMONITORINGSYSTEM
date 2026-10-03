"""
Simple local API test after starting Flask.
Run:
    python test_api.py
"""

import json
from urllib.request import Request, urlopen

payload = {
    "soil_moisture": 43,
    "temperature": 31,
    "humidity": 55,
}

request = Request(
    "http://127.0.0.1:5000/api/predict",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urlopen(request) as response:
    print(response.read().decode("utf-8"))
