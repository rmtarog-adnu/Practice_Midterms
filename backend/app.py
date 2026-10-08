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
    password_hash = generate_password_hash(password)
    role = data.get("role")

    connection = get_db_connection()

    try:

        connection.execute("""
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

        return jsonify({
            "message": "Registration successful."
        }), 201

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 400

    finally:

        connection.close()


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

@app.route("/api/records", methods=["GET"])
def get_records():

    search = request.args.get("search", "").strip()

    connection = get_db_connection()

    if search:

        records = connection.execute("""
            SELECT * FROM records
            WHERE name LIKE ?
               OR description LIKE ?
               OR category LIKE ?
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    else:

        records = connection.execute("""
            SELECT * FROM records
        """).fetchall()

    connection.close()

    record_list = []

    for record in records:

        record_list.append({
            "id": record["id"],
            "name": record["name"],
            "description": record["description"],
            "category": record["category"]
        })

    return jsonify({
        "records": record_list
    })

if __name__ == "__main__":
    app.run(debug=True)