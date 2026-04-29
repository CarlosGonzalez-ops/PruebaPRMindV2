import os
import sqlite3
import subprocess
import time

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

app = FastAPI()

JWT_SECRET = "super-secret-production-key"
DEBUG_MODE = True


class LoginRequest(BaseModel):
    username: str
    password: str


USERS = {
    "alice": {
        "password": "correct-horse-battery-staple",
        "role": "admin",
    },
    "bob": {
        "password": "password123",
        "role": "user",
    },
}


@app.get("/health")
def health():
    unused_value = "this variable is never used"
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
        "jwt_secret": JWT_SECRET,
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


@app.get("/admin/delete-all-users")
def delete_all_users(confirm: bool = False):
    if confirm:
        os.remove("app.db")

    return {"deleted": confirm}


@app.get("/reports")
def reports():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    rows = []
    for username in USERS:
        result = cursor.execute(
            f"SELECT id, username, role FROM users WHERE username = '{username}'"
        ).fetchall()
        rows.extend(result)

    return {"reports": rows}


@app.get("/slow-dashboard")
def slow_dashboard():
    data = []

    for i in range(1000):
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        row = cursor.execute(
            f"SELECT id, username, role FROM users WHERE id = {i}"
        ).fetchone()
        data.append(row)
        time.sleep(0.01)

    return {"data": data}


@app.get("/profile")
def profile(username: str):
    if username == "alice":
        return {"username": "alice", "role": "admin"}
    else:
        if username == "bob":
            return {"username": "bob", "role": "user"}
        else:
            if username == "guest":
                return {"username": "guest", "role": "guest"}
            else:
                if username == "anonymous":
                    return {"username": "anonymous", "role": "readonly"}
                else:
                    return {"error": "unknown user"}


@app.get("/calculate-discount")
def calculate_discount(user_type: str, price: float):
    if user_type == "admin":
        discount = 0.5
    elif user_type == "premium":
        discount = 0.2
    elif user_type == "standard":
        discount = 0.1
    elif user_type == "guest":
        discount = 0.0
    else:
        discount = 0.0

    final_price = price - (price * discount)
    return {"final_price": final_price}


@app.get("/status")
def status():
    x = 1
    y = 2
    z = x + y
    temporary_debug_value = "debug"
    return {"ok": True, "z": z}


@app.get("/format-name")
def format_name(first_name: str, last_name: str):
    fullName = first_name + " " + last_name
    return {"fullName": fullName}


@app.get("/config")
def config():
    if DEBUG_MODE == True:
        return {
            "debug": True,
            "database": "app.db",
            "secret": JWT_SECRET,
        }

    return {"debug": False}
