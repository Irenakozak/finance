import tkinter as tk
from tkinter import ttk
import requests
import mysql.connector
import time
import iso18245

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="finance"
)

window = tk.Tk()
window.title("Фінансовий менеджер")
window.geometry("500x400")

tab_control = ttk.Notebook(window)

tab_total_expenses = ttk.Frame(tab_control)
tab_control.add(tab_total_expenses, text="Загальна сума витрат")

tab_statement = ttk.Frame(tab_control)
tab_control.add(tab_statement, text="Виписка транзакцій")

tab_category_statistics = ttk.Frame(tab_control)
tab_control.add(tab_category_statistics, text="Статистика по категоріям")

tab_control.pack(expand=1, fill="both")

def clear_tables():
    mycursor = mydb.cursor()
    sql = "TRUNCATE TABLE AllTransactions"
    mycursor.execute(sql)
    mydb.commit()
    
    mycursor = mydb.cursor()
    sql = "TRUNCATE TABLE IncomingTransactions"
    mycursor.execute(sql)
    mydb.commit()

    mycursor = mydb.cursor()
    sql = "TRUNCATE TABLE OutgoingTransactions"
    mycursor.execute(sql)
    mydb.commit()

def show_total_expenses(client_info):
    user_id = client_info["clientId"]
    mycursor = mydb.cursor()
    sql = "SELECT SUM(amount) FROM AllTransactions WHERE user_id = %s AND amount < 0"
    val = (user_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    total_expenses = result[0] if result[0] else 0
    total_expenses = float(total_expenses) / 100.00
    total_expenses_label.configure(text=f"Загальна сума витрат за місяць:  {total_expenses} грн")

def show_statement(client_info):
    user_id = client_info["clientId"]
    mycursor = mydb.cursor()
    sql = "SELECT mcc, amount, description FROM AllTransactions WHERE user_id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    transactions = mycursor.fetchall()
    
    statement_text.delete("1.0", "end")
    for transaction in transactions:
        mcc, amount, description = transaction
        amount = float(amount) / 100.00
        category = iso18245.get_mcc(str(mcc)).range.description
        statement_text.insert("end", f"Категорія: {category}\n")
        statement_text.insert("end", f"MCC: {mcc}, Сума: {amount} грн, Опис: {description}\n\n")

def show_category_statistics(client_info):
    user_id = client_info["clientId"]
    mycursor = mydb.cursor()
    sql = "SELECT mcc, SUM(amount) FROM AllTransactions WHERE user_id = %s GROUP BY mcc"
    val = (user_id,)
    mycursor.execute(sql, val)
    category_transactions = mycursor.fetchall()

    category_statistics_text.delete("1.0", "end")
    for category_transaction in category_transactions:
        mcc, total_amount = category_transaction
        total_amount = float(total_amount) / 100.00
        category = iso18245.get_mcc(str(mcc)).range.description
        category_statistics_text.insert("end", f"Категорія: {category}\n")
        category_statistics_text.insert("end", f"MCC: {mcc}, {'Загальна сума витрат: ' if total_amount < 0 else 'Сума прибутку з категорії: '} {total_amount} грн\n\n")

def get_client_info(x_token):
    headers = {
        "X-Token": x_token
    }
    response = requests.get("https://api.monobank.ua/personal/client-info", headers=headers)
    client_info = response.json()
    return client_info

def save_user(user_id, name, email, password, x_token):
    mycursor = mydb.cursor()
    sql = "INSERT INTO Users (id, name, email, password, x_token) VALUES (%s, %s, %s, %s, %s)"
    val = (user_id, name, email, password, x_token)
    mycursor.execute(sql, val)
    mydb.commit()

def get_user_input():
    name = input("Введіть ваше ім'я: ")
    email = input("Введіть вашу електронну пошту: ")
    password = input("Введіть пароль: ")
    x_token = input("Введіть ваш x-token: ")
    return name, email, password, x_token

def check_user_exists(user_id):
    mycursor = mydb.cursor()
    sql = "SELECT id FROM Users WHERE id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    return result is not None

def get_statement(account, from_time, to_time, x_token):
    headers = {
        "X-Token": x_token
    }
    url = f"https://api.monobank.ua/personal/statement/{account}/{from_time}/{to_time}"
    response = requests.get(url, headers=headers)
    statement = response.json()
    return statement

def save_transactions(account, x_token):
    clear_tables()
    mycursor = mydb.cursor()
    sql = "INSERT INTO AllTransactions (user_id, amount, description, transaction_id, transaction_date, mcc) VALUES (%s, %s, %s, %s, %s, %s)"
    
    from_time = int(time.time()) - 30 * 24 * 60 * 60  # 30 днів у секундах
    to_time = int(time.time())
    headers = {
        "X-Token": x_token
    }
    statement = get_statement(account, from_time, to_time, x_token)
    response = requests.get("https://api.monobank.ua/personal/client-info", headers=headers)
    client_info = response.json()
    for transaction in statement:
        user_id = client_info["clientId"]
        amount = transaction["amount"]
        description = transaction["description"]
        transaction_id = transaction["id"]
        transaction_date = transaction["time"]
        mcc = transaction["mcc"]
        val = (user_id, amount, description, transaction_id, transaction_date, mcc)
        mycursor.execute(sql, val)
    mydb.commit()

def register_user():
    root = tk.Tk()
    root.title("Реєстрація та вхід у систему")

    def register():
        name = name_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        x_token = x_token_entry.get()
        headers = {
            "X-Token": x_token
        }
        response = requests.get("https://api.monobank.ua/personal/client-info", headers=headers)
        client_info = response.json()
        user_id = client_info["clientId"]
        save_user(user_id, name, email, password, x_token)
        print("Реєстрація успішна. Дані користувача збережено.")
        client_info = get_client_info(x_token)
        save_transactions(0, x_token)
        show_total_expenses(client_info)
        show_statement(client_info)
        show_category_statistics(client_info)
        root.destroy()

    def login():
        email = email_entry.get()
        password = password_entry.get()
        mycursor = mydb.cursor()
        sql = "SELECT * FROM users WHERE email = %s AND password = %s"
        val = (email, password)
        mycursor.execute(sql, val)
        x_token = list(mycursor.fetchall()[0])[4]
        print(x_token)
        if x_token is None:
            print("Неправильний email або пароль. Будь ласка, спробуйте ще раз.")
            return
        print("Вхід у систему успішний.")
        client_info = get_client_info(x_token)
        save_transactions(0, x_token)
        show_total_expenses(client_info)
        show_statement(client_info)
        show_category_statistics(client_info)
        root.destroy()
    name_label = tk.Label(root, text="Ім'я:")
    name_label.pack()
    name_entry = tk.Entry(root)
    name_entry.pack()
    email_label = tk.Label(root, text="Email:")
    email_label.pack()
    email_entry = tk.Entry(root)
    email_entry.pack()
    password_label = tk.Label(root, text="Пароль:")
    password_label.pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()
    x_token_label = tk.Label(root, text="X-Token (тільки для реєстрації):")
    x_token_label.pack()
    x_token_entry = tk.Entry(root, show="*")
    x_token_entry.pack()
    register_button = tk.Button(root, text="Реєстрація", command=register)
    register_button.pack()
    login_button = tk.Button(root, text="Вхід у систему", command=login)
    login_button.pack()
    root.mainloop()


total_expenses_label = ttk.Label(tab_total_expenses, text="")
total_expenses_label.pack(pady=10)
statement_text = tk.Text(tab_statement)
statement_text.pack(pady=10)
category_statistics_text = tk.Text(tab_category_statistics)
category_statistics_text.pack(pady=10)
register_user()
window.mainloop()
mydb.close()
