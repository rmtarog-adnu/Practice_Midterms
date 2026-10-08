from flask import Flask, jsonify, request
from database import get_db_connection, init_db

app = Flask(__name__)

init_db()


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
            password,
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
        WHERE id_number = ? AND password_hash = ?
    """, (
        id_number,
        password
    )).fetchone()

    connection.close()

    if user:

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
# GET RECORDS
# =========================

@app.route("/api/records", methods=["GET"])
def get_records():

    connection = get_db_connection()

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