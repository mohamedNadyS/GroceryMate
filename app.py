import streamlit as st
import passlib.context
import mysql.connector
import time
import secrets
import string

pwd_hash = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")

def connect_db():
    conn = mysql.connector.connect(**st.secrets["mysql"])
    cursor = conn.cursor()
    return cursor, conn
    
def close_db(cursor,connection):
    cursor.close()
    connection.close()

def add_user(username,gmail,password):
    cursor, conn = connect_db()
    searcher = "SELECT * FROM users WHERE username = %s"
    cursor.execute(searcher, (username,))
    results = cursor.fetchall()
    if results:
        return False
    sql = "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) PRIMARY KEY,gmail VARCHAR(255), password VARCHAR(255),in_group BOOLEAN DEFAULT FALSE, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    cursor.execute(sql)
    sql = "INSERT INTO users (username,gmail,password) VALUES (%s,%s,%s)"
    cursor.execute(sql, (username,gmail,pwd_hash.hash(password)))
    conn.commit()
    close_db(cursor,conn)
    return True

def create_join_code(length = 8):
    code = ''.join(secrets.choice(string.ascii_letters+string.digits)for _ in range(length))
    return code
secrets.choice
def create_group(group_name,username):
    #need add roles system like manager (auto fro creator) admin, member later
    cursor, conn = connect_db()
    sql = "CREATE TABLE IF NOT EXISTS groups (group_name VARCHAR(255),join_code VARCHAR(10) PRIMARY KEY,created_by VARCHAR(255), timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    cursor.execute(sql)
    conn.commit()
    while True:
        code = create_join_code()
        sql = "SELECT * FROM groups WHERE join_code =%s"
        cursor.execute(sql,(code,))
        if not cursor.fetchone():
            break
    sql = "INSERT INTO groups (group_name,join_code,created_by) VALUES (%s,%s,%s)"
    values = (group_name,code,username)
    cursor.execute(sql,values)
    conn.commit()
    close_db(cursor,conn)
    join_group(username,code)
    return code



def join_group(username,join_code):
    cursor,conn=connect_db()
    sql = "CREATE TABLE IF NOT EXISTS group_members (member_id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), group_name VARCHAR(255),join_code VARCHAR(10),joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (username) REFERENCES users(username),FOREIGN KEY (join_code) REFERENCES groups(join_code))"
    cursor.execute(sql)
    sql = "SELECT * FROM groups WHERE join_code =%s"
    cursor.execute(sql,(join_code,))
    row = cursor.fetchone()
    if not row:
        return False
    group_name = row[0]
    sql = "INSERT INTO group_members (username,group_name,join_code) VALUES (%s,%s,%s)"
    values =(username,group_name,join_code)
    cursor.execute(sql,values)
    sql = "UPDATE users SET in_group=TRUE WHERE username = %s"
    values = (username,)
    cursor.execute(sql,values)
    conn.commit()
    close_db(cursor,conn)
    return group_name

def remove_from_group(username,group_name):
    cursor,conn=connect_db()
    sql = "DELETE FROM group_members WHERE username=%s AND group_name=%s"
    values = (username,group_name)
    cursor.execute(sql,values)
    conn.commit()
    close_db(cursor,conn)


def verify_password(plain_password,hashed_password):
    return pwd_hash.verify(plain_password,hashed_password)

def authenticate_user(username,password):
    cursor, conn = connect_db()
    sql = "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) PRIMARY KEY,gmail VARCHAR(255), password VARCHAR(255),in_group BOOLEAN DEFAULT FALSE, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    cursor.execute(sql)
    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (username,))
    results = cursor.fetchone()
    close_db(cursor,conn)
    if not results:
        return "User Not found"
    if verify_password(password,results[2]):
        return "Login Success"
    else:
        return "Wrong password"

def check_in_group(username):
    cursor,conn = connect_db()
    sql = "SELECT in_group FROM users WHERE username =%s"
    cursor.execute(sql,(username,))
    result = cursor.fetchone()
    close_db(cursor,conn)
    if result is None:
        return False
    if result[0]:
        return True
    else:
        return False

def add_item(username,item,quantity,unit,importance,category,notes):
    cursor, conn = connect_db()
    sql = "CREATE TABLE IF NOT EXISTS items (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), item VARCHAR(255), quantity INT, unit VARCHAR(255), importance VARCHAR(255), shop VARCHAR(255),category VARCHAR(255), notes TEXT, unavailable BOOLEAN DEFAULT FALSE,purchased BOOLEAN DEFAULT FALSE,timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (username) REFERENCES users(username))"
    cursor.execute(sql)
    sql = "INSERT INTO items (username,item,quantity,unit,importance,category,notes) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    values = (username,item,quantity,unit,importance,category,notes)
    cursor.execute(sql, values)
    conn.commit()
    close_db(cursor,conn)
    return True


def change_password(username,new_password):
    cursor,conn = connect_db()
    sql = "UPDATE users SET password = %s WHERE username=%s"
    values = (pwd_hash.hash(new_password),username)
    cursor.execute(sql,values)
    conn.commit()
    close_db(cursor,conn)
    return True

def check_user(username):
    cursor,conn = connect_db()
    sql = "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) PRIMARY KEY,gmail VARCHAR(255), password VARCHAR(255),in_group BOOLEAN DEFAULT FALSE, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    cursor.execute(sql)
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
    username =""
    group_name = ""
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    def go_to(page):
        st.session_state.page = page

    st.title("GroceryMate")
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
        gmail = st.text_input("Gmail",help="Enter a valid Gmail address.")
        
        password = st.text_input("password",type="password",help="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
        confirm_password = st.text_input("confirm password",type="password",help="Re-enter your password to confirm.")
        if st.button("signup"):
            if password != confirm_password:
                st.warning("Passwords do not match.")
            elif "@" not in gmail or ".com" not in gmail:
                st.warning("Please enter a valid Gmail address.")
            elif len(password) < 8:
                st.warning("Password must be at least 8 characters long.")
            elif not any(char.isupper() for char in password):
                st.warning("Password must contain at least one uppercase letter.")
            elif not any(char.islower() for char in password):
                st.warning("Password must contain at least one lowercase letter.")
            elif not any(char.isdigit() for char in password):
                st.warning("Password must contain at least one digit.")
            elif not any(char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for char in password):
                st.warning("Password must contain at least one special character.")
            elif 5>len(username) or len(username)>20:
                st.warning("Username must be between 5 to 20 characters long.")
            elif password and confirm_password and username:
                if add_user(username,gmail,password):
                    st.success("Account created successfully!")
                    go_to("login")
                    st.rerun()
                    
                else:
                    st.warning("Username already exists. Please choose a different username.")
        else:
            st.error("Please fill in all fields.")


    def create_group_ui():
        group_name = st.text_input("Your group name")
        col1,col2,col3,col4 = st.columns(4)
        with col3:
            if st.button("Create group"):
                code = create_group(group_name,username)
                st.write("this your group join code: ",code)
        with col4:
            if st.button("Cancel",type="tertiary"):
                go_to(home)
                st.rerun

    def add_item_ui():
        with st.form(key='item',clear_on_submit=True):
            item_name=st.text_input("Insert your item here")
            quantity = st.number_input("quantity of the item",min_value=1,step=1)
            options = ["kg","g","Ib","oz","m","cm","in","ft","pcs","ml","l","gal"]
            unit = st.selectbox("unit of item quantity",options,help="kg is kilogram, g is gram, ib is pound, oz is ounce, m is centimetre, cm is centimetre, in is inch, ft is feet, pcs is pieces, ml is milliliter, l in liter, gal is gallon")
            optionsI = ["Urgent","important","Normal","not-important"]
            importance = st.selectbox("the importance of the item",optionsI)
            optionsC = ["Produce","Meat & Seafood","Dairy","Bakery","Frozen Foods","Pantry","Snacks","Beverages","Household Supplies","Health & Beauty/Pharmacy","Baby Products","Pet Supplies"]
            category = st.selectbox("The category of grocery item",optionsC)
            notes = st.text_area("notes/description")
            col1,col2,col3,col4 = st.columns(4)
            with col3:
                submit = st.form_submit_button("Add",type='primary')
            with col4:
                if st.button("Cancel",type="tertiary"):
                    go_to(home)
                    st.rerun
        if submit:
            if not item_name:
                st.error("item field is required")
            elif not quantity:
                st.error("quantity field is required")
            elif not unit:
                st.error("unit field is required")
            elif not importance:
                st.error("importance field is required")
            elif not category:
                st.error("category field is required")
            elif not notes:
                st.error("notes/description field is required")
            elif add_item(username,item_name,quantity,unit,importance,category,notes):
                st.success("Add successfully")
                time.sleep(2)
                go_to(home)
                st.rerun            


    def leave_group_ui():
        remove_from_group(username,group_name)
        go_to(home)
        st.rerun


    def join_group_ui():
        with st.form(key='group',clear_on_submit=True):
            group_code = st.text_input("Enter group joining code")
            col1,col2,col3,col4 = st.columns(4)
            with col3:
                submit = st.form_submit_button("join",type='primary')
            with col4:
                if st.button("Cancel",type="tertiary"):
                    go_to(home)
                    st.rerun
        if submit:
            if not group_code:
                st.error("this field is required")
            else:
                group_name = join_group(username,group_code)
        
    def home():
        if check_in_group(username):
            pages = [st.Page(leave_group_ui,title="leave group"),st.Page(add_item_ui,title="Add item"),st.Page(login,title="logout")]
        else:
            pages = [st.Page(create_group_ui,title="create group"),st.Page(join_group_ui,title="join group"),st.Page(add_item_ui,title="Add item"),st.Page(login,title="logout")]
        st.subheader("Share your grocery list with mates")
        st.navigation(pages,position="top")


    if st.session_state.page == "login":
        login()
    if st.session_state.page == "signup":
        signup()
    if st.session_state.page == "home":
        home()


if __name__ == "__main__":
    main()