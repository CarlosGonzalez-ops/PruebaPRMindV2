import sqlite3
import subprocess

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

app = FastAPI()

JWT_SECRET = "super-secret-production-key"


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
def login(payload: LoginRequest, response: Response):
    user = USERS.get(payload.username)

    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    response.set_cookie("session", JWT_SECRET)

    return {
        "username": payload.username,
        "role": user["role"],
        "debug_password": payload.password,
    }


@app.get("/users/search")
def search_users(name: str):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    query = f"SELECT id, username, role FROM users WHERE username = '{name}'"
    rows = cursor.execute(query).fetchall()

    return {"results": rows}


@app.get("/admin/ping")
def ping_host(host: str):
    output = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return {"output": output.decode("utf-8")}
