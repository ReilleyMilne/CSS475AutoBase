from flask import Blueprint, jsonify, request, session
from dotenv import load_dotenv
from database import get_db_connection

load_dotenv()

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login for both employees and customers"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user_type = data.get('user_type')

    # Validate required fields
    if not all([username, password, user_type]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate user_type
    if user_type not in ['employee', 'customer']:
        return jsonify({'error': 'Invalid user type'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Query the appropriate table based on user type
        if user_type == 'employee':
            cursor.execute("SELECT * FROM EmployeeAuth WHERE Username = %s", (username,))
            id_field = 'Employee_ID'
        else:
            cursor.execute("SELECT * FROM CustomerAuth WHERE Username = %s", (username,))
            id_field = 'Customer_ID'

        user = cursor.fetchone()

        # Check if user exists and password matches
        if user and user['Password_Hash'] == password:
            # Create user session data
            user_data = {
                'username': username,
                'user_type': user_type,
                'id': user[id_field]
            }
            
            # Store in session
            session.permanent = False
            session['user'] = user_data
            session.modified = True
            
            print(f"Login successful: {username} ({user_type})")
            
            return jsonify({
                'message': 'Login successful',
                'user': user_data
            }), 200
        else:
            print(f"Login failed: {username} ({user_type})")
            return jsonify({'error': 'Invalid credentials'}), 401

    finally:
        cursor.close()
        conn.close()


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    username = session.get('user', {}).get('username', 'Unknown')
    session.pop('user', None)
    session.modified = True
    
    print(f"Logout: {username}")
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/current_user', methods=['GET'])
def current_user():
    """Get the currently logged-in user from session"""
    user = session.get('user')
    
    if user:
        print(f"Session check: {user['username']} ({user['user_type']})")
        return jsonify({'user': user}), 200
    else:
        print("No active session")
        return jsonify({'user': None}), 200