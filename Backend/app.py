from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv() 

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
}

@app.route('/primary_key/<table_name>')
def get_primary_key(table_name):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = %s
              AND CONSTRAINT_NAME = 'PRIMARY';
        """
        cursor.execute(query, (table_name,))
        result = cursor.fetchone()
        return jsonify(result if result else {"error": "No primary key found"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route("/tables", methods=["GET"])
def get_all_tables():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Query INFORMATION_SCHEMA to get all tables in the current database
        query = """
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = %s
        """
        cursor.execute(query, (db_config['database'],))
        tables = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        return jsonify(tables)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
        

@app.route("/<table_name>", methods=["GET"])
def get_table_data(table_name):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
    