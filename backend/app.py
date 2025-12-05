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
DB_DRIVER = os.getenv("DB_DRIVER")

# Build connection string
CONNECTION_STRING = f"""
    Server={DB_SERVER};
    Driver={DB_DRIVER};
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

def normalize_keys(row):
    return {k.lower(): v for k, v in row.items()}


@app.route("/")
def home():
    print("Home endpoint hit!")
    return jsonify({"status": "alive"})

@app.route("/brands/")
def get_brands():
    limit = request.args.get("limit", default=10, type=int)
    limit = max(1, min(limit, 1000))
    query = f"SELECT TOP {limit} * FROM dbo.BrandDetails;"
    result = fetch_as_dicts(execute_query(query))
    if result is None:
        return jsonify({"error": "Database error"}), 500
    
    return result 


@app.route("/daily-spend/")
def get_daily_spend():
    limit = request.args.get("limit", default=10, type=int)
    limit = max(1, min(limit, 1000))
    query = f"SELECT TOP {limit} * FROM dbo.BrandTransactions ORDER BY SPEND_AMOUNT DESC;"
    result = fetch_as_dicts(execute_query(query))
    if result is None:
        return jsonify({"error": "Database error"}), 500
    
    return result 

@app.route("/summary/")
def get_summary():
    try:
        # Overall spend stats
        query_overall = """
        SELECT 
            SUM(SPEND_AMOUNT) AS total_spend,
            AVG(SPEND_AMOUNT) AS avg_transaction_amount,
            MAX(SPEND_AMOUNT) AS max_spend,
            MIN(SPEND_AMOUNT) AS min_spend
        FROM dbo.BrandTransactions;
        """
        overall_stats = execute_query(query_overall)
        if not overall_stats:
            raise ValueError("No overall stats returned")

        # Top 10 brands by spend
        query_brands = """
        SELECT TOP 10
            b.BRAND_ID,
            b.BRAND_NAME,
            SUM(t.SPEND_AMOUNT) AS total_spend,
            AVG(t.SPEND_AMOUNT) AS avg_spend,
            COUNT(*) AS num_transactions
        FROM dbo.BrandTransactions t
        JOIN dbo.BrandDetails b ON t.BRAND_ID = b.BRAND_ID
        GROUP BY b.BRAND_ID, b.BRAND_NAME
        ORDER BY total_spend DESC;
        """
        top_brands = execute_query(query_brands) or []

        # Spend by industry
        query_by_industry = """
        SELECT 
            b.INDUSTRY_NAME,
            SUM(t.SPEND_AMOUNT) AS total_spend
        FROM dbo.BrandTransactions t
        JOIN dbo.BrandDetails b ON t.BRAND_ID = b.BRAND_ID
        GROUP BY b.INDUSTRY_NAME
        ORDER BY total_spend DESC;
        """
        spend_by_industry = execute_query(query_by_industry) or []

        # Spend by state
        query_by_state = """
        SELECT 
            t.STATE_ABBR,
            SUM(t.SPEND_AMOUNT) AS total_spend
        FROM dbo.BrandTransactions t
        GROUP BY t.STATE_ABBR
        ORDER BY total_spend DESC;
        """
        spend_by_state = execute_query(query_by_state) or []

        # Transaction count by industry
        query_tx_by_industry = """
        SELECT 
            b.INDUSTRY_NAME,
            COUNT(*) AS transaction_count
        FROM dbo.BrandTransactions t
        JOIN dbo.BrandDetails b ON t.BRAND_ID = b.BRAND_ID
        GROUP BY b.INDUSTRY_NAME
        ORDER BY transaction_count DESC;
        """
        tx_count_by_industry = execute_query(query_tx_by_industry) or []

        # Normalize keys
        overall_stats_normalized = normalize_keys(overall_stats[0])
        top_brands_normalized = [normalize_keys(b) for b in top_brands]
        spend_by_industry_normalized = [normalize_keys(b) for b in spend_by_industry]
        spend_by_state_normalized = [normalize_keys(b) for b in spend_by_state]
        tx_count_by_industry_normalized = [normalize_keys(b) for b in tx_count_by_industry]

        return jsonify({
            "overall_stats": overall_stats_normalized,
            "top_brands": top_brands_normalized,
            "spend_by_industry": spend_by_industry_normalized,
            "spend_by_state": spend_by_state_normalized,
            "tx_count_by_industry": tx_count_by_industry_normalized
        })

    except Exception as e:
        print("Flask summary endpoint error:", e)
        return jsonify({"error": "Database error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)