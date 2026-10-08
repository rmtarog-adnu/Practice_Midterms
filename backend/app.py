from flask import Flask, jsonify
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


if __name__ == "__main__":
    app.run(debug=True)