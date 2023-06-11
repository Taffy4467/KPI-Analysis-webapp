import requests
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import json
import pymysql


# Create a dictionary to store the content for each option
option_content = {
    "Home": {
        "title": "Welcome to the Department KPI Web App!",
        "subtitle": "This app provides powerful data analysis and visualization tools for your organization.",
        "description": "",
        "animations": [
            "https://assets4.lottiefiles.com/packages/lf20_QrXB6LUk3W.json",
            "https://assets2.lottiefiles.com/packages/lf20_twnj9fob.json",
            "https://assets5.lottiefiles.com/packages/lf20_u8jppxsl.json"
        ]
    },
    "Upload": {
        "title": "Upload your Excel files and let the app analyze and visualize the data.",
        "animations": [
            "https://assets5.lottiefiles.com/packages/lf20_bdlrkrqv.json",
            "https://assets9.lottiefiles.com/packages/lf20_uaYKb6.json"
        ]
    },
    "Tasks": {
        "title": "App Tasks",
        "subtitle": "Perform various tasks and operations on your data with ease.",
        "description": [
            {
                "text": "Task 1: Import data from Excel file",
                "animation": "https://assets10.lottiefiles.com/packages/lf20_9mq0wl6b.json"
            },
            {
                "text": "Task 2: Clean and preprocess data",
                "animation": "https://assets8.lottiefiles.com/packages/lf20_x17ybolp.json"
            },
            {
                "text": "Task 3: Apply data analysis techniques",
                "animation": "https://assets8.lottiefiles.com/packages/lf20_9wpyhdzo.json"
            },
            {
                "text": "Task 4: Visualize and present results",
                "animation": "https://assets8.lottiefiles.com/packages/lf20_dews3j6m.json"
            }
        ]
    },
    "Get started": {
        "redirect": True
    }
}

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
    # 2. horizontal menu
    selected_option = option_menu(None, list(option_content.keys()),
                                  icons=['house', 'cloud-upload', "list-task"],
                                  menu_icon="cast", default_index=0,
                                  orientation="horizontal")

    # Render the content based on the selected option
    content = option_content[selected_option]

    # Set the title of the app
    content['title'] = 'Department KPI Web App'

    st.title(content["title"])

    if "subtitle" in content:
        st.write(content["subtitle"])
    if "description" in content:
        for item in content["description"]:
            if "text" in item:
                st.write(item["text"])
            if "animation" in item:
                lottie_json = requests.get(item["animation"]).json()
                st_lottie(lottie_json, height=200, width=900)
    if "animations" in content:
        animations = content["animations"]
        style = "<style>div.row-widget.stRadio > div{flex-direction:row;}</style>"
        st.markdown(style, unsafe_allow_html=True)
        for animation_url in animations:
            lottie_json = requests.get(animation_url).json()
            st_lottie(lottie_json, height=200, width=500)

    if selected_option == "Get started":
        login_registration_page()


def login_registration_page():
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