import requests

url = "http://127.0.0.1:5000/api/analyze"

with open("data.zip", "rb") as f:
    files = {
        "file": ("data.zip", f)
    }

    response = requests.post(url, files=files)

print(response.status_code)
print(response.json())