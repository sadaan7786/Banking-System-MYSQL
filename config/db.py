import mysql.connector
import os

DB_CONFIG = {
    'host':     os.getenv('DB_HOST',     'localhost'),
    'port':     int(os.getenv('DB_PORT', 3306)),
    'user':     os.getenv('DB_USER',     'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME',     'banking_system'),
    'autocommit': False,
}

def get_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

def init_db():
    # Connect without a database first to create it
    cfg = {k: v for k, v in DB_CONFIG.items() if k != 'database' and k != 'autocommit'}
    conn = mysql.connector.connect(**cfg)
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute(f"USE `{DB_CONFIG['database']}`")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            CustomerID   INT          AUTO_INCREMENT PRIMARY KEY,
            FullName     VARCHAR(150) NOT NULL,
            CNIC         VARCHAR(20)  NOT NULL UNIQUE,
            MobileNumber VARCHAR(20)  NOT NULL UNIQUE,
            Email        VARCHAR(150),
            Password     VARCHAR(255) NOT NULL,
            IsApproved   TINYINT(1)   DEFAULT 0,
            IsAdmin      TINYINT(1)   DEFAULT 0,
            CreatedAt    DATETIME     DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            AccountID    INT          AUTO_INCREMENT PRIMARY KEY,
            CustomerID   INT          NOT NULL,
            AccountType  VARCHAR(50)  NOT NULL DEFAULT 'Digital Wallet',
            Balance      DECIMAL(15,2) DEFAULT 0.00,
            CreatedAt    DATETIME     DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            TransactionID INT           AUTO_INCREMENT PRIMARY KEY,
            AccountID     INT           NOT NULL,
            Type          VARCHAR(10)   NOT NULL,
            Amount        DECIMAL(15,2) NOT NULL,
            Description   VARCHAR(255),
            CreatedAt     DATETIME      DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (AccountID) REFERENCES accounts(AccountID)
        )
    """)

    # Seed admin if not exists
    cursor.execute("SELECT CustomerID FROM customers WHERE MobileNumber='03001234567'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO customers (FullName, CNIC, MobileNumber, Email, Password, IsApproved, IsAdmin)
            VALUES ('Admin User', '00000-0000000-0', '03001234567', 'admin@bank.com', 'admin123', 1, 1)
        """)
        admin_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO accounts (CustomerID, AccountType, Balance) VALUES (%s, %s, %s)",
            (admin_id, 'Digital Wallet', 50000.00)
        )
        acc_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO transactions (AccountID, Type, Amount, Description) VALUES (%s, %s, %s, %s)",
            (acc_id, 'Credit', 50000.00, 'Opening balance')
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("✓ MySQL database initialised")
