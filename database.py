import sqlite3


def init_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()


    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, role TEXT, 
                  first_name TEXT, last_name TEXT, phone_number TEXT)''')


    c.execute('''CREATE TABLE IF NOT EXISTS categories 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')


    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category_id INTEGER, price REAL,
                  FOREIGN KEY(category_id) REFERENCES categories(id))''')

    conn.commit()
    conn.close()


def get_db_connection():
    return sqlite3.connect('shop.db')