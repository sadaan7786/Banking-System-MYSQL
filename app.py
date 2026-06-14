from flask import Flask, send_from_directory
from flask_cors import CORS
from api.customers import customers_bp
from api.accounts import accounts_bp
from api.transactions import transactions_bp
from api.admin import admin_bp
from config.db import init_db

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

app.register_blueprint(customers_bp,    url_prefix='/api/customers')
app.register_blueprint(accounts_bp,     url_prefix='/api/accounts')
app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
app.register_blueprint(admin_bp,        url_prefix='/api/admin')

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
