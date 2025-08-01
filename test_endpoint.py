from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/user/{user_id}/profile")
def user_profile(user_id: str):
    return {"status": "success", "user": {"id": user_id, "name": "Test User"}}

client = TestClient(app)
response = client.get("/api/user/test_user_123/profile")
print("Status:", response.status_code)
print("Data:", response.json()) 