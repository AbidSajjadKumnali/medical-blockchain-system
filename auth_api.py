from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from auth.auth import login_user, register_user
import json
import uuid
app = Flask(__name__)
CORS(app)
@app.route("/")
def home():
    return send_file("static/login_page.html")
@app.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data.get("username")
    password = data.get("password")

    success, message, user_data = login_user(
        username,
        password
    )

    if success:

        session_id = str(uuid.uuid4())

        with open("login_sessions.json", "r") as f:
            sessions = json.load(f)

        sessions[session_id] = user_data

        with open("login_sessions.json", "w") as f:
            json.dump(sessions, f)

        return jsonify({
            "success": True,
            "session_id": session_id
        })

    return jsonify({
        "success": False,
        "message": message
    })
@app.route("/register", methods=["POST"])
def register():

    data = request.json

    success, message = register_user(
        username=data.get("username"),
        email=data.get("email"),
        password=data.get("password"),
        confirm_password=data.get("confirm_password"),
        role=data.get("role", "patient"),
        age=data.get("age", 0),
        blood_group=data.get("blood_group", "O+"),
        allergies=data.get("allergies", ""),
        emergency_contact=data.get("emergency_contact", "")
    )

    return jsonify({
        "success": success,
        "message": message
    })

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )