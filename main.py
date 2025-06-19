# main.py
from dotenv import load_dotenv
load_dotenv()

import os
import json
from fastapi import FastAPI
from db import get_connection
from openai import OpenAI

# OpenAI 1.x istemcisi
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

# --- 1) Fonksiyon Tanımları ---
FUNC_DEFS = [
    {
        "name": "addUser",
        "description": "Veritabanına yeni bir kullanıcı ekler.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string",  "description": "Kullanıcı adı"},
                "age":  {"type": "integer", "description": "Kullanıcı yaşı"}
            },
            "required": ["name", "age"]
        },
        "return": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "userId":  {"type": "integer"}
            }
        }
    },
    {
        "name": "getUsers",
        "description": "Tüm kullanıcıları listeler.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
        "return": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id":          {"type": "integer"},
                    "name":        {"type": "string"},
                    "age":         {"type": "integer"},
                    "created_at":  {"type": "string"}
                }
            }
        }
    },
    {
        "name": "deleteUser",
        "description": "Veritabanından bir kullanıcıyı siler.",
        "parameters": {
            "type": "object",
            "properties": {
                "userId": {"type": "integer", "description": "Silinecek kullanıcının ID'si"}
            },
            "required": ["userId"]
        },
        "return": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "description": "Silme işleminin başarısı"}
            }
        }
    }
]

# --- 2) Chat Endpoint ---
@app.post("/chat")
async def chat_endpoint(payload: dict):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=payload["messages"],
        functions=FUNC_DEFS,
        function_call="auto"
    )
    choice = resp.choices[0].message

    if choice.function_call:
        name = choice.function_call.name
        args = json.loads(choice.function_call.arguments)
        result = await dispatch(name, args)
        return {"tool_result": result}

    return {"reply": choice.content}

# --- 3) Dispatch Logic ---
async def dispatch(name: str, args: dict):
    if name == "addUser":
        return add_user(args["name"], args["age"])
    elif name == "getUsers":
        return get_users()
    elif name == "deleteUser":
        return delete_user(args["userId"])
    else:
        return {"error": f"Unknown tool: {name}"}

# --- 4) Handler Fonksiyonları ---
def add_user(name: str, age: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, age) VALUES (%s, %s)",
                (name, age)
            )
            user_id = cur.lastrowid
        conn.commit()
        return {"success": True, "userId": user_id}
    finally:
        conn.close()

def get_users():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, age, created_at FROM users")
            return cur.fetchall()
    finally:
        conn.close()

def delete_user(user_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            success = cur.rowcount > 0
        conn.commit()
        return {"success": success}
    finally:
        conn.close()
