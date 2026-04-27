from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class LoginRequest(BaseModel):
    username: str
    password: str


USERS = {
    "alice": {
        "password": "correct-horse-battery-staple",
        "role": "admin",
    }
}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/login")
def login(payload: LoginRequest):
    user = USERS.get(payload.username)

    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "username": payload.username,
        "role": user["role"],
    }
