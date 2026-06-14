from flask import Blueprint, jsonify
from config.db import get_db

accounts_bp = Blueprint('accounts', __name__)

@accounts_bp.route('/<int:customer_id>/accounts')
def get_accounts(customer_id):
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM accounts WHERE CustomerID=%s ORDER BY AccountID",
        (customer_id,)
    )
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    # Convert Decimal to float for JSON serialisation
    for r in rows:
        r['Balance'] = float(r['Balance'])
    return jsonify(rows)

@accounts_bp.route('/<int:account_id>/transactions')
def get_transactions(account_id):
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM transactions WHERE AccountID=%s ORDER BY CreatedAt DESC LIMIT 100",
        (account_id,)
    )
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    for r in rows:
        r['Amount'] = float(r['Amount'])
        if r.get('CreatedAt'):
            r['CreatedAt'] = r['CreatedAt'].isoformat()
    return jsonify(rows)
