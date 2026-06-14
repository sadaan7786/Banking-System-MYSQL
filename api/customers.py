from flask import Blueprint, request, jsonify
from config.db import get_db

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/login', methods=['POST'])
def login():
    data     = request.get_json()
    mobile   = (data.get('MobileNumber') or '').strip()
    password = (data.get('Password') or '').strip()
    if not mobile or not password:
        return jsonify({'error': 'Mobile number and password are required.'}), 400

    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM customers WHERE MobileNumber=%s AND Password=%s",
        (mobile, password)
    )
    row = cursor.fetchone()
    cursor.close(); conn.close()

    if not row:
        return jsonify({'error': 'Invalid mobile number or password.'}), 401
    if not row['IsApproved']:
        return jsonify({'error': 'Your account is pending admin approval.'}), 403

    return jsonify({
        'CustomerID': row['CustomerID'],
        'FullName':   row['FullName'],
        'IsAdmin':    bool(row['IsAdmin'])
    })

@customers_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    for f in ['FullName', 'CNIC', 'MobileNumber', 'Password']:
        if not (data.get(f) or '').strip():
            return jsonify({'error': f'{f} is required.'}), 400

    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT CustomerID FROM customers WHERE MobileNumber=%s OR CNIC=%s",
        (data['MobileNumber'].strip(), data['CNIC'].strip())
    )
    if cursor.fetchone():
        cursor.close(); conn.close()
        return jsonify({'error': 'Mobile number or CNIC already registered.'}), 409

    cursor.execute(
        "INSERT INTO customers (FullName, CNIC, MobileNumber, Email, Password) VALUES (%s,%s,%s,%s,%s)",
        (data['FullName'].strip(), data['CNIC'].strip(), data['MobileNumber'].strip(),
         data.get('Email', '').strip(), data['Password'])
    )
    cust_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO accounts (CustomerID, AccountType, Balance) VALUES (%s, %s, %s)",
        (cust_id, 'Digital Wallet', 0.00)
    )
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({'message': 'Registration successful. Awaiting admin approval.'}), 201
