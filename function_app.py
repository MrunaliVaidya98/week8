import os
import pyodbc
import azure.functions as func

from flask import Flask, jsonify, request, render_template


# --------------------------------------------------
# FLASK APPLICATION
# --------------------------------------------------

flask_app = Flask(__name__)


# --------------------------------------------------
# AZURE SQL DATABASE CONNECTION
# --------------------------------------------------

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


# --------------------------------------------------
# CHECK LOGIN CREDENTIALS
# --------------------------------------------------

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


# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------

@flask_app.route("/", methods=["GET"])
def home():

    return render_template("login.html")


# --------------------------------------------------
# LOGIN API
# --------------------------------------------------

@flask_app.route("/login", methods=["POST"])
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

        else:

            return jsonify({
                "success": False,
                "message": "Invalid username or password"
            }), 401

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# --------------------------------------------------
# TEST DATABASE CONNECTION
# --------------------------------------------------

@flask_app.route("/test-db", methods=["GET"])
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


# --------------------------------------------------
# CONNECT FLASK TO AZURE FUNCTIONS
# --------------------------------------------------

app = func.WsgiFunctionApp(
    app=flask_app.wsgi_app,
    http_auth_level=func.AuthLevel.ANONYMOUS
)
