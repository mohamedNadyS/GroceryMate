import streamlit as st
import passlib.context
import mysql.connector
import time

pwd_hash = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")

def connect_db():
    conn = mysql.connector.connect(**st.secrets["mysql"])
    cursor = conn.cursor()
    return cursor, conn
    
def close_db(cursor,connection):
    cursor.close()
    connection.close()

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
    close_db(cursor,conn)
    return True

def verify_password(plain_password,hashed_password):
    return pwd_hash.verify(plain_password,hashed_password)

def authenticate_user(username,password):
    cursor, conn = connect_db()
    sql = "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255), timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    cursor.execute(sql)
    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (username,))
    results = cursor.fetchone()
    close_db(cursor,conn)
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
    close_db(cursor,conn)
    return True

def check_user(username):
    cursor,conn = connect_db()
    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (username,))
    results = cursor.fetchall()
    close_db(cursor,conn)
    if results:
        return True
    return False
def mark_done(username,item):
    cursor,conn = connect_db()
    sql = "UPDATE items SET done = TRUE WHERE username= %s AND item = %s"
    values = (username,item)
    cursor.execute(sql,values)
    conn.commit()
    close_db(cursor,conn)
    return True

def remove_item(username,item):
    cursor,conn = connect_db()
    sql = "DELETE FROM items WHERE username= %s AND item = %s"
    values = (username,item)
    cursor.execute(sql,values)
    conn.commit()
    close_db(cursor,conn)
    return True

def view_items(username):
    cursor, conn = connect_db()
    sql = "SELECT * FROM items WHERE username = %s"
    cursor.execute(sql, (username,))
    results = cursor.fetchall()
    close_db(cursor,conn)
    return results

def main():
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    def go_to(page):
        st.session_state.page = page

    st.title("GroceryMate")
    st.subheader("Share your grocery list with mates")
    def login():
        st.subheader("Login to your account")
        username = st.text_input("username")
        password = st.text_input("password",type="password")
        st.login = st.button("Login")
        if st.login:
            if authenticate_user(username,password) == "Login Success":
                
                st.success("Login successful!")
                time.sleep(1)
                go_to("home")
                st.rerun()
            elif authenticate_user(username,password) == "User Not found":
                st.warning("User not found. Please sign up first if you don't have an account or write the true username.")
            elif authenticate_user(username,password) == "Wrong password":
                st.warning("Wrong password. Please try again.")
        col1, col2,col3,col4 = st.columns(4)
        with col1:
            st.write("New to GroceryMate?")
        with col2:
            st.button("SignUp", on_click=go_to, args=("signup",), type="secondary")

    def signup():
        st.subheader("Create a new account")
        username = st.text_input("username",help="Username must be between 5 to 20 characters long.")
        if len(username) < 5 or len(username) > 20:
            st.warning("Username must be between 5 to 20 characters long.")
        if check_user(username):
            st.warning("Username already exists. Please choose a different username.")
        
        password = st.text_input("password",type="password",help="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
        confirm_password = st.text_input("confirm password",type="password",help="Re-enter your password to confirm.")
        if st.button("signup"):
            if password != confirm_password:
                st.warning("Passwords do not match.")
            elif len(password) < 8:
                st.warning("Password must be at least 8 characters long.")
            elif not any(char.isupper() for char in password):
                st.warning("Password must contain at least one uppercase letter.")
            elif not any(char.islower() for char in password):
                st.warning("Password must contain at least one lowercase letter.")
            elif not any(char.isdigit() for char in password):
                st.warning("Password must contain at least one digit.")
            elif not any(char in "!@#$%^&*()-_=+[{]}\|;:'\",<.>/?`~" for char in password):
                st.warning("Password must contain at least one special character.")
            elif 5>len(username) or len(username)>20:
                st.warning("Username must be between 5 to 20 characters long.")
            elif password and confirm_password and username:
                if add_user(username,password):
                    st.success("Account created successfully!")
                    go_to("login")
                    st.rerun()
                    
                else:
                    st.warning("Username already exists. Please choose a different username.")
        else:
            st.error("Please fill in all fields.")

    def home():
        pass

    if st.session_state.page == "login":
        login()
    if st.session_state.page == "signup":
        signup()
    if st.session_state.page == "home":
        home()


if __name__ == "__main__":
    main()