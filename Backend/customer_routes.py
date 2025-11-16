from flask import Blueprint, jsonify, session
from db_utils import ( 
    execute_query
)

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/vehicles', methods=['GET'])
def get_customer_vehicles():
    user = session.get('user')
    if not user or user.get('user_type') != 'customer':
        return jsonify({'error': 'Unauthorized'}), 401
    
    customer_id = user.get('id')

    try:
        query = """
            SELECT Vehicle.*
            FROM Vehicle
            JOIN CustomerOwnVehicle ON CustomerOwnVehicle.Vehicle_VIN = Vehicle.VIN
            JOIN Customer ON Customer.ID = CustomerOwnVehicle.Customer_ID
            JOIN CustomerAuth ON CustomerAuth.Customer_ID = Customer.ID
            WHERE Customer.ID = %s
            Order By Vehicle.Year DESC;
        """

        vehicles = execute_query(query, (customer_id,))
        
        if vehicles is None:
            return jsonify({'error': 'Failed to fetch vehicles'}), 500
        
        print(f"Fetched {len(vehicles)} vehicles for customer {customer_id}")
        return jsonify({'vehicles': vehicles}), 200
        
    except Exception as e:
        print(f"Error in get_customer_vehicles: {str(e)}")
        return jsonify({'error': 'Failed to fetch vehicles'}), 500


@customer_bp.route('/vehicle/<vin>', methods=['GET'])
def get_vehicle_details(vin):
    user = session.get('user')
    if not user or user.get('user_type') != 'customer':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        query = """
            SELECT Vehicle.*
            FROM Vehicle
            JOIN CustomerOwnVehicle ON CustomerOwnVehicle.Vehicle_VIN = Vehicle.VIN
            JOIN Customer ON Customer.ID = CustomerOwnVehicle.Customer_ID
            JOIN CustomerAuth ON CustomerAuth.Customer_ID = Customer.ID
            WHERE Vehicle.VIN = %s
            Order By Vehicle.Year DESC;
        """

        vehicle = execute_query(query, (vin,), fetch_one=True)
        
        if vehicle:
            print(f"Fetched details for vehicle {vin}")
            return jsonify({'vehicle': vehicle}), 200
        else:
            return jsonify({'error': 'Vehicle not found'}), 404
            
    except Exception as e:
        print(f"Error in get_vehicle_details: {str(e)}")
        return jsonify({'error': 'Failed to fetch vehicle details'}), 500


@customer_bp.route('/info', methods=['GET'])
def get_customer_info():
    user = session.get('user')
    if not user or user.get('user_type') != 'customer':
        return jsonify({'error': 'Unauthorized'}), 401
    
    customer_id = user.get('id')
    
    try:
        query = """
            SELECT Customer.Name, Customer.Phone, Customer.Email, Customer.Address, Customer.Gender, Customer.Registration_Date
            FROM Customer
            JOIN CustomerAuth ON CustomerAuth.Customer_ID = Customer.ID
            WHERE Customer.ID = %s;
        """

        customer = execute_query(query, (customer_id,), fetch_one=True)
        
        if customer:
            print(f"Fetched details for customer {customer_id}")
            return jsonify({'customer': customer}), 200
        else:
            return jsonify({'error': 'Customer not found'}), 404
            
    except Exception as e:
        print(f"Error in get_customer_info: {str(e)}")
        return jsonify({'error': 'Failed to fetch customer details'}), 500