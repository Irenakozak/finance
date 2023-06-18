create database if not exists finance;
use finance;
SET FOREIGN_KEY_CHECKS=0;

drop table if exists users;

drop table if exists AllTransactions;

drop table if exists IncomingTransactions;

drop table if exists OutgoingTransactions;

SET FOREIGN_KEY_CHECKS=1;

CREATE TABLE Users (
  id VARCHAR(100) PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  email VARCHAR(50) NOT NULL,
  password VARCHAR(50) NOT NULL,
  x_token VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы "Все транзакции"
CREATE TABLE AllTransactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(100) NOT NULL,
  amount NUMERIC NOT NULL,
  description VARCHAR(100),
  transaction_id VARCHAR(100) NOT NULL,
  transaction_date VARCHAR(100) NOT NULL,
  mcc NUMERIC NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- Создание таблицы "Входящие транзакции"
CREATE TABLE IncomingTransactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(100) NOT NULL,
  sender_name VARCHAR(50) NOT NULL,
  amount NUMERIC NOT NULL,
  description VARCHAR(100),
  transaction_id VARCHAR(100) NOT NULL,
  transaction_date VARCHAR(100) NOT NULL,
  mcc NUMERIC NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- Создание таблицы "Исходящие транзакции"
CREATE TABLE OutgoingTransactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(100) NOT NULL,
  recipient_name VARCHAR(50) NOT NULL,
  amount NUMERIC NOT NULL,
  description VARCHAR(100),
  transaction_id VARCHAR(100) NOT NULL,
  transaction_date VARCHAR(100) NOT NULL,
  mcc NUMERIC NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES Users(id)
);

ALTER TABLE AllTransactions
    ADD COLUMN is_outgoing BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN is_incoming BOOLEAN NOT NULL DEFAULT FALSE;

DELIMITER $$
CREATE TRIGGER trg_outgoing_transaction
BEFORE INSERT ON AllTransactions
FOR EACH ROW
BEGIN
    IF NEW.amount < 0 THEN
        INSERT INTO OutgoingTransactions (user_id, recipient_name, amount, description, transaction_id, transaction_date, mcc)
        VALUES (NEW.user_id, '', NEW.amount, NEW.description, NEW.transaction_id, NEW.transaction_date, NEW.mcc);
    END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER trg_incoming_transaction
BEFORE INSERT ON AllTransactions
FOR EACH ROW
BEGIN
    IF NEW.amount > 0 THEN
        INSERT INTO IncomingTransactions (user_id, sender_name, amount, description, transaction_id, transaction_date, mcc)
        VALUES (NEW.user_id, '', NEW.amount, NEW.description, NEW.transaction_id, NEW.transaction_date, NEW.mcc);
    END IF;
END$$
DELIMITER ;