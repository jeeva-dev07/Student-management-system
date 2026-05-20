import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="velmurugan2002", 
            database="student_management"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def validate_student_data(data):
    if not data or not data.get('full_name') or len(data['full_name'].strip()) < 2:
        return "Invalid or missing full name."
    if not data.get('email') or not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return "Invalid email address."
    if not data.get('phone') or len(data['phone'].strip()) < 7:
        return "Invalid phone number."
    if not data.get('course') or len(data['course'].strip()) == 0:
        return "Course selection is required."
    return None

@app.route('/api/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, full_name, email, phone, course, DATE_FORMAT(enrolled_on, '%Y-%m-%d') as enrolled_on FROM students ORDER BY id DESC")
        students = cursor.fetchall()
        cursor.close()
        return jsonify(students), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to fetch student records"}), 500
    finally:
        conn.close()

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()
    validation_error = validate_student_data(data)
    if validation_error:
        return jsonify({"error": validation_error}), 400
        
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        cursor = conn.cursor()
        query = "INSERT INTO students (full_name, email, phone, course) VALUES (%s, %s, %s, %s)"
        values = (data['full_name'].strip(), data['email'].strip(), data['phone'].strip(), data['course'].strip())
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        return jsonify({"message": "Student registered successfully!"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already exists."}), 409
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to register student due to a server error."}), 500
    finally:
        conn.close()

@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    validation_error = validate_student_data(data)
    if validation_error:
        return jsonify({"error": validation_error}), 400
        
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        cursor = conn.cursor()
        query = "UPDATE students SET full_name = %s, email = %s, phone = %s, course = %s WHERE id = %s"
        values = (data['full_name'].strip(), data['email'].strip(), data['phone'].strip(), data['course'].strip(), student_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        return jsonify({"message": "Student updated successfully."}), 200
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already in use."}), 409
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to update student due to a server error."}), 500
    finally:
        conn.close()

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
        cursor.close()
        return jsonify({"message": "Student removed successfully."}), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to delete student record."}), 500
    finally:
        conn.close()

@app.route('/api/students/search', methods=['GET'])
def search_students():
    query_param = request.args.get('q', '').strip()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    try:
        cursor = conn.cursor(dictionary=True)
        sql_query = "SELECT id, full_name, email, phone, course, DATE_FORMAT(enrolled_on, '%Y-%m-%d') as enrolled_on FROM students WHERE full_name LIKE %s OR course LIKE %s ORDER BY id DESC"
        search_pattern = f"%{query_param}%"
        cursor.execute(sql_query, (search_pattern, search_pattern))
        results = cursor.fetchall()
        cursor.close()
        return jsonify(results), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Search operation failed."}), 500
    finally:
        conn.close()

@app.route('/')
def home():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
