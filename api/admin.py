from flask import Blueprint, request, jsonify
from config.db import get_db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/pending-customers')
def pending():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT CustomerID,FullName,CNIC,MobileNumber,Email,CreatedAt FROM customers WHERE IsApproved=0 ORDER BY CreatedAt"
    )
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    for r in rows:
        if r.get('CreatedAt'):
            r['CreatedAt'] = r['CreatedAt'].isoformat()
    return jsonify(rows)

@admin_bp.route('/all-customers')
def all_customers():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT CustomerID,FullName,CNIC,MobileNumber,Email,IsApproved,IsAdmin,CreatedAt FROM customers ORDER BY CreatedAt"
    )
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    for r in rows:
        if r.get('CreatedAt'):
            r['CreatedAt'] = r['CreatedAt'].isoformat()
    return jsonify(rows)

@admin_bp.route('/approve-customer', methods=['POST'])
def approve():
    data    = request.get_json()
    cust_id = data.get('CustomerID')
    action  = data.get('Action', '')
    if not cust_id or action not in ('Approve', 'Reject'):
        return jsonify({'error': 'CustomerID and Action (Approve/Reject) are required.'}), 400

    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    if action == 'Approve':
        cursor.execute("UPDATE customers SET IsApproved=1 WHERE CustomerID=%s", (cust_id,))
        # Give welcome bonus if balance is 0
        cursor.execute("SELECT AccountID, Balance FROM accounts WHERE CustomerID=%s LIMIT 1", (cust_id,))
        acc = cursor.fetchone()
        if acc and float(acc['Balance']) == 0:
            cursor.execute("UPDATE accounts SET Balance=1000 WHERE AccountID=%s", (acc['AccountID'],))
            cursor.execute(
                "INSERT INTO transactions (AccountID,Type,Amount,Description) VALUES (%s,%s,%s,%s)",
                (acc['AccountID'], 'Credit', 1000.00, 'Welcome bonus from SmartPayBank')
            )
    else:
        cursor.execute("DELETE FROM accounts WHERE CustomerID=%s", (cust_id,))
        cursor.execute("DELETE FROM customers WHERE CustomerID=%s", (cust_id,))

    conn.commit()
    cursor.close(); conn.close()
    return jsonify({'message': f'Customer {action.lower()}d successfully.'})
