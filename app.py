import streamlit as st
import passlib.context
import mysql.connector
import time

pwd_hash = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")

def connect_db():
    conn = mysql.connector.connect(**st.secrets["mysql"])
    cursor = conn.cursor()
    return cursor, conn
    
def close_db(cursor):
    cursor.close()
    cursor.connection.close()

def add_user(username,password):
    cursor, conn = connect_db()
    searcher = "SELECT * FROM users WHERE username = %s"
    cursor.execute(searcher, (username,))
    results = cursor.fetchall()
    if results:
        return False
    sql = "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255), timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    values = (username,pwd_hash.hash(password))
    cursor.execute(sql)
    sql = "INSERT INTO users (username,password) VALUES (%s,%s)"
    cursor.execute(sql, values)
    conn.commit()
    close_db(cursor)
    return True

def verify_password(plain_password,hashed_password):
    return pwd_hash.verify(plain_password,hashed_password)

def authenticate_user(username,password):
    cursor, conn = connect_db()
    sql = "SELECT * FROM users WHERE username = '%s'"
    cursor.execute(sql, (username,))
    results = cursor.fetchone()
    close_db(cursor)
    if not results:
        return "User Not found"
    if verify_password(password,results[1]):
        return "Login Success"
    else:
        return "Wrong password"

def add_item(username,item,quantity):
    cursor, conn = connect_db()
    sql = "CREATE TABLE IF NOT EXISTS items (username VARCHAR(255) PRIMARY KEY, item VARCHAR(255), quantity INT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, done BOOLEAN DEFAULT FALSE, FOREIGN KEY (username) REFERENCES users(username))"
    cursor.execute(sql)
    sql = "INSERT INTO items (username,item,quantity) VALUES (%s,%s,%s)"
    values = (username,item,quantity)
    cursor.execute(sql, values)
    conn.commit()
    close_db(cursor)
    return True

def mark_done(username,item):
    cursor,conn = connect_db()
    sql = "UPDATE items SET done = TRUE WHERE username= %s AND item = %s"
    values = (username,item)
    cursor.execute(sql,values)
    conn.commit()
    close_db(cursor)
    return True

def remove_item(username,item):
    cursor,conn = connect_db()
    sql = "DELETE FROM items WHERE username= %s AND item = %s"
    values = (username,item)
    cursor.execute(sql,values)
    conn.commit()
    close_db(cursor)
    return True

def view_items(username):
    cursor, conn = connect_db()
    sql = "SELECT * FROM items WHERE username = %s"
    cursor.execute(sql, (username,))
    results = cursor.fetchall()
    close_db(cursor)
    return results
