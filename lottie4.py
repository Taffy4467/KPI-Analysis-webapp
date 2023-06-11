import requests
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import json

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

# 2. horizontal menu
selected_option = option_menu(None, list(option_content.keys()),
                              icons=['house', 'cloud-upload', "list-task"],
                              menu_icon="cast", default_index=0,
                              orientation="horizontal")

# Render the content based on the selected option
content = option_content[selected_option]

if "redirect" in content:
    # Redirect to the user login and registration page
    st.text("Redirect to user login and registration page")
else:
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
