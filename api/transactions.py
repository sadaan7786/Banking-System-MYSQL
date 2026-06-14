from flask import Blueprint, request, jsonify
from config.db import get_db

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transfer', methods=['POST'])
def transfer():
    data        = request.get_json()
    from_acc_id = data.get('FromAccountID')
    to_mobile   = (data.get('ToMobileNumber') or '').strip()
    amount      = float(data.get('Amount', 0))
    description = data.get('Description') or data.get('TransactionType') or 'Transfer'

    if not from_acc_id or not to_mobile or amount <= 0:
        return jsonify({'error': 'FromAccountID, ToMobileNumber, and a positive Amount are required.'}), 400

    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    # Lock sender account
    cursor.execute("SELECT * FROM accounts WHERE AccountID=%s FOR UPDATE", (from_acc_id,))
    sender_acc = cursor.fetchone()
    if not sender_acc:
        cursor.close(); conn.close()
        return jsonify({'error': 'Sender account not found.'}), 404
    if float(sender_acc['Balance']) < amount:
        cursor.close(); conn.close()
        return jsonify({'error': 'Insufficient balance.'}), 400

    # Find recipient by mobile
    cursor.execute(
        "SELECT c.CustomerID FROM customers c WHERE c.MobileNumber=%s AND c.IsApproved=1",
        (to_mobile,)
    )
    recipient = cursor.fetchone()
    if not recipient:
        cursor.close(); conn.close()
        return jsonify({'error': 'Recipient not found or not yet approved.'}), 404

    cursor.execute(
        "SELECT AccountID FROM accounts WHERE CustomerID=%s LIMIT 1",
        (recipient['CustomerID'],)
    )
    recipient_acc = cursor.fetchone()
    if not recipient_acc:
        cursor.close(); conn.close()
        return jsonify({'error': 'Recipient has no account.'}), 404

    # Debit sender
    cursor.execute(
        "UPDATE accounts SET Balance = Balance - %s WHERE AccountID=%s",
        (amount, from_acc_id)
    )
    cursor.execute(
        "INSERT INTO transactions (AccountID, Type, Amount, Description) VALUES (%s,%s,%s,%s)",
        (from_acc_id, 'Debit', amount, f"Transfer to {to_mobile} — {description}")
    )

    # Credit recipient
    cursor.execute(
        "UPDATE accounts SET Balance = Balance + %s WHERE AccountID=%s",
        (amount, recipient_acc['AccountID'])
    )
    cursor.execute(
        "INSERT INTO transactions (AccountID, Type, Amount, Description) VALUES (%s,%s,%s,%s)",
        (recipient_acc['AccountID'], 'Credit', amount, f"Transfer from acc#{from_acc_id} — {description}")
    )

    conn.commit()
    cursor.close(); conn.close()
    return jsonify({'message': 'Transfer successful.'})
