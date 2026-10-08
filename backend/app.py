import logging

from flask import Flask, jsonify, request
from database import get_db_connection, init_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

logging.basicConfig(
    filename="backend/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

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

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "error": "Resource not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({
        "error": "Method not allowed."
    }), 405


@app.errorhandler(500)
def internal_server_error(error):

    return jsonify({
        "error": "Internal server error."
    }), 500

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

    logger.info("User registered successfully: %s", id_number)

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

    try:

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

        logger.info("Record created successfully: ID %s", record_id)

        return jsonify({
            "message": "Record created successfully.",
            "record": {
                "id": record_id,
                "name": name,
                "description": description,
                "category": category
            }
        }), 201

    except Exception as error:

        connection.rollback()
        connection.close()

        return jsonify({
            "error": "Failed to create record."
        }), 500

# =========================
# UPDATE RECORD
# =========================

@app.route("/api/records/<int:record_id>", methods=["PUT"])
@role_required("admin", "teacher")
def update_record(record_id):

    data = request.get_json()

    name = data.get("name")
    description = data.get("description")
    category = data.get("category")

    if not name:
        return jsonify({
            "error": "Name is required."
        }), 400

    connection = get_db_connection()

    try:

        record = connection.execute("""
            SELECT * FROM records
            WHERE id = ?
        """, (record_id,)).fetchone()

        if not record:
            connection.close()

            return jsonify({
                "error": "Record not found."
            }), 404

        connection.execute("""
            UPDATE records
            SET name = ?, description = ?, category = ?
            WHERE id = ?
        """, (
            name,
            description,
            category,
            record_id
        ))

        connection.commit()

        logger.info("Record updated successfully: ID %s", record_id)

        connection.close()

        return jsonify({
            "message": "Record updated successfully.",
            "record": {
                "id": record_id,
                "name": name,
                "description": description,
                "category": category
            }
        }), 200

    except Exception as error:

        connection.rollback()
        connection.close()

        return jsonify({
            "error": "Failed to update record."
        }), 500

# =========================
# DELETE RECORD
# =========================

@app.route("/api/records/<int:record_id>", methods=["DELETE"])
@role_required("admin", "teacher")
def delete_record(record_id):

    connection = get_db_connection()

    try:

        record = connection.execute("""
            SELECT * FROM records
            WHERE id = ?
        """, (record_id,)).fetchone()

        if not record:
            connection.close()

            return jsonify({
                "error": "Record not found."
            }), 404

        connection.execute("""
            DELETE FROM records
            WHERE id = ?
        """, (record_id,))

        connection.commit()

        logger.info("Record deleted successfully: ID %s", record_id)

        connection.close()

        return jsonify({
            "message": "Record deleted successfully."
        }), 200

    except Exception as error:

        connection.rollback()
        connection.close()

        return jsonify({
            "error": "Failed to delete record."
        }), 500
    
# =========================
# GET RECORDS WITH SEARCH
# =========================

@app.route("/api/records", methods=["GET"])
@role_required("admin", "teacher", "student")
def get_records():

    search = request.args.get("search", "").strip()

    connection = get_db_connection()

    try:

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
        }), 200

    except Exception as error:

        connection.close()

        return jsonify({
            "error": "Failed to retrieve records."
        }), 500

if __name__ == "__main__":
    app.run(debug=True)