import requests
import json

# Test with a local file or URL
test_url = "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png"

payload = {
    "document": test_url
}

response = requests.post(
    "http://localhost:8000/extract-bill-data",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print("Status Code:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2))