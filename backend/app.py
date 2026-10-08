from flask import Flask, jsonify, request
from database import get_db_connection, init_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

init_db()

def role_required(*allowed_roles):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            role = request.headers.get("Role")

            if role not in allowed_roles:

                return jsonify({
                    "error": "Access denied."
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator

@app.route("/")
def home():

    connection = get_db_connection()
    connection.close()

    return jsonify({
        "message": "Mini Management System API is running.",
        "database": "Connected"
    })


# =========================
# REGISTER
# =========================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    id_number = data.get("id_number")
    name = data.get("name")
    email = data.get("email")
    contact = data.get("contact")
    password = data.get("password")
    role = data.get("role")

    # Validate required fields BEFORE hashing
    if not id_number or not name or not email or not password or not role:
        return jsonify({
            "error": "Required fields are missing."
        }), 400

    # Hash password after validation
    password_hash = generate_password_hash(password)

    connection = get_db_connection()

    try:

        cursor = connection.execute("""
            INSERT INTO users
            (id_number, name, email, contact, password_hash, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            id_number,
            name,
            email,
            contact,
            password_hash,
            role
        ))

        connection.commit()

    except Exception as error:

        connection.close()

        return jsonify({
            "error": str(error)
        }), 400

    connection.close()

    return jsonify({
        "message": "Registration successful."
    }), 201


# =========================
# LOGIN
# =========================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    id_number = data.get("id_number")
    password = data.get("password")

    connection = get_db_connection()

    user = connection.execute("""
    SELECT * FROM users
    WHERE id_number = ?
""", (
    id_number,
)).fetchone()

    connection.close()

    if user and check_password_hash(user["password_hash"], password):

        return jsonify({
            "message": "Login successful.",
            "user": {
                "id_number": user["id_number"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        })

    return jsonify({
        "error": "Invalid ID number or password."
    }), 401

# =========================
# CREATE RECORD
# =========================

@app.route("/api/records", methods=["POST"])
@role_required("admin", "teacher")
def create_record():

    data = request.get_json()

    name = data.get("name")
    description = data.get("description")
    category = data.get("category")

    if not name:
        return jsonify({
        "error": "Name is required."
    }), 400

    connection = get_db_connection()

    cursor = connection.execute("""
        INSERT INTO records
        (name, description, category)
        VALUES (?, ?, ?)
    """, (
        name,
        description,
        category
    ))

    connection.commit()

    record_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "message": "Record created successfully.",
        "record": {
            "id": record_id,
            "name": name,
            "description": description,
            "category": category
        }
    }), 201

# =========================
# GET RECORDS WITH SEARCH
# =========================


if __name__ == "__main__":
    app.run(debug=True)