from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import pyodbc

load_dotenv()

app = Flask(__name__)
CORS(app)

load_dotenv()

# Load DB credentials from environment variables
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Build connection string
CONNECTION_STRING = f"""
Driver=/usr/local/lib/libmsodbcsql.18.dylib;
Server={DB_SERVER};
Database={DB_NAME};
Uid={DB_USER};
Pwd={DB_PASSWORD};
Encrypt=yes;
TrustServerCertificate=no;
Connection Timeout=30;
"""

def get_connection():
    """Create a new database connection"""
    try:
        print(f"Attempting to connect to: {DB_SERVER}")
        conn = pyodbc.connect(CONNECTION_STRING)
        print("Database connection successful!")
        return conn
    except pyodbc.Error as e:
        print(f"Database connection failed!")
        print(f"Error: {e}")
        # Print more details
        if hasattr(e, 'args') and len(e.args) > 1:
            print(f"Error code: {e.args[0]}")
            print(f"Error message: {e.args[1]}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def execute_query(query, params=None):
    """Helper to execute a query safely and fetch results as dicts"""
    print(f"\nExecuting query: {query}")
    if params:
        print(f"With params: {params}")
    
    conn = get_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = fetch_as_dicts(cursor)
            print(f"Query returned {len(result)} rows")
            return result
    except pyodbc.Error as e:
        print(f"Query execution failed!")
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during query: {e}")
        return None
    finally:
        conn.close()
        print("Connection closed")

def fetch_as_dicts(cursor):
    """Helper to convert cursor results to list of dicts"""
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def execute_query(query, params=None):
    """Helper to execute a query safely and fetch results as dicts"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return fetch_as_dicts(cursor)
    except Exception as e:
        print("Database error:", e)
        return None
    finally:
        conn.close()

@app.route("/brands/")
def get_brands():
    limit = request.args.get("limit", default=20, type=int)
    # Validate limit to prevent issues
    limit = max(1, min(limit, 1000))  # Between 1 and 1000
    
    query = "SELECT TOP (?) * FROM dbo.BrandDetails"
    result = execute_query(query, (limit,))
    
    if result is None:
        return jsonify({"error": "Database error"}), 500
    return jsonify(result)

@app.route("/daily-spend/")
def get_daily_spend():
    limit = request.args.get("limit", default=20, type=int)
    limit = max(1, min(limit, 1000))
    
    query = "SELECT TOP (?) * FROM dbo.BrandTransactions"
    result = execute_query(query, (limit,))
    
    if result is None:
        return jsonify({"error": "Database error"}), 500
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)