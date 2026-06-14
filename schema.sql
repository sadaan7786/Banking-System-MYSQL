CREATE DATABASE IF NOT EXISTS banking_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE banking_system;

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
);

CREATE TABLE IF NOT EXISTS accounts (
    AccountID   INT            AUTO_INCREMENT PRIMARY KEY,
    CustomerID  INT            NOT NULL,
    AccountType VARCHAR(50)    NOT NULL DEFAULT 'Digital Wallet',
    Balance     DECIMAL(15,2)  DEFAULT 0.00,
    CreatedAt   DATETIME       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)
);

CREATE TABLE IF NOT EXISTS transactions (
    TransactionID INT            AUTO_INCREMENT PRIMARY KEY,
    AccountID     INT            NOT NULL,
    Type          VARCHAR(10)    NOT NULL,
    Amount        DECIMAL(15,2)  NOT NULL,
    Description   VARCHAR(255),
    CreatedAt     DATETIME       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (AccountID) REFERENCES accounts(AccountID)
);

-- Default admin account (password: admin123)
INSERT IGNORE INTO customers (FullName, CNIC, MobileNumber, Email, Password, IsApproved, IsAdmin)
VALUES ('Admin User', '00000-0000000-0', '03001234567', 'admin@bank.com', 'admin123', 1, 1);
