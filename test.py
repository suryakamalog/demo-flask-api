import requests

BASE = "http://0.0.0.0:5001/"
body = {"first_name": "Amit",
        "last_name": "Kumar",
        "email": "suryakamalog1@gmail.com",
        "phone": "8294310527"}
response = requests.post(BASE + "user", json = body)
print(response.json())