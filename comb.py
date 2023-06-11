import pymysql
import streamlit as st

# Connect to the database
myconn = pymysql.connect(
    host="localhost",
    user="root",
    password="NB-2405-@mysql23!",
    database="excelwebapp",
    cursorclass=pymysql.cursors.DictCursor  # Use DictCursor to get results as dictionaries
)

# Create a cursor object
cursor = myconn.cursor()


def register_user(username, password):
    try:
        # Use parameterized query to insert user data
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        myconn.commit()
        return True
    except pymysql.Error as e:
        # Handle any errors that occur during the execution of the query
        print(f"Error registering user: {e}")
        return False


def login_user(username, password):
    try:
        # Use parameterized query to fetch user data
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        return result is not None
    except pymysql.Error as e:
        # Handle any errors that occur during the execution of the query
        print(f"Error logging in: {e}")
        return False


def main():
    st.sidebar.title("User Management")
    choice = st.sidebar.radio("Select an option", ("Login", "Registration"))

    if choice == "Registration":
        st.title("User Registration")

        # User registration
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_button = st.button("Register")

        if reg_button:
            if register_user(reg_username, reg_password):
                st.success("User registered successfully.")
            else:
                st.error("Failed to register user.")

    elif choice == "Login":
        st.title("User Login")

        # User login
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        login_button = st.button("Login")

        if login_button:
            if login_user(login_username, login_password):
                st.success("User logged in successfully.")
            else:
                st.error("Login failed.")


if __name__ == '__main__':
    main()
