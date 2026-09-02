import os
import pyodbc

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


def get_database_connection():

    server = os.environ.get("SQL_SERVER")
    database = os.environ.get("SQL_DATABASE")
    username = os.environ.get("SQL_USERNAME")
    password = os.environ.get("SQL_PASSWORD")

    connection_string = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server=tcp:{server},1433;"
        f"Database={database};"
        f"Uid={username};"
        f"Pwd={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    return pyodbc.connect(connection_string)


def check_credentials(username, password):

    query = """
        SELECT 1
        FROM dbo.[user]
        WHERE username = ? AND password = ?
    """

    with get_database_connection() as connection:

        cursor = connection.cursor()

        cursor.execute(
            query,
            (username, password)
        )

        return cursor.fetchone() is not None


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not username or not password:

        return jsonify({
            "success": False,
            "message": "Username and password are required"
        }), 400

    try:

        if check_credentials(username, password):

            return jsonify({
                "success": True,
                "message": "Login successful"
            }), 200

        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/test-db")
def test_db():

    try:

        with get_database_connection() as connection:

            cursor = connection.cursor()

            cursor.execute("SELECT DB_NAME()")

            database_name = cursor.fetchone()[0]

        return jsonify({
            "message": "Database connection successful",
            "database": database_name
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)