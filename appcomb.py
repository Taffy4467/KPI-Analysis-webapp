import requests
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import json
import pymysql
import os
import pandas as pd
import numpy as np
import plotly.express as px
import base64
from io import BytesIO
import uuid
import plotly.graph_objects as go

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
        "Animations": [
            "https://assets9.lottiefiles.com/packages/lf20_uaYKb6.json"
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
        print(f"Error logging in user: {e}")
        return False


def get_uploaded_files():
    try:
        query = "SHOW COLUMNS FROM uploaded_files;"
        cursor.execute(query)
        columns = [column["Field"] for column in cursor.fetchall() if column["Field"].startswith("file_name")]
        files = []

        for column in columns:
            query = f"SELECT DISTINCT `{column}` FROM uploaded_files"
            cursor.execute(query)
            file_column = cursor.fetchall()
            files.extend([file["file_name"] for file in file_column])

        return files
    except pymysql.Error as e:
        # Handle any errors that occur during the execution of the query
        print(f"Error retrieving uploaded files: {e}")
        return []


def generate_excel_download_link(df):
    towrite = BytesIO()
    df.to_excel(towrite, index=False, header=True)
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File</a>'
    return href


def main():
    st.set_page_config(page_title="KPI Analysis")

    page_options = list(option_content.keys())
    page_choice = option_menu("Select a page", page_options)

    if page_choice in option_content:
        page = option_content[page_choice]
        st.title(page.get("title", ""))
        st.subheader(page.get("subtitle", ""))
        st.markdown(page.get("description", ""))

        animations = page.get("animations", [])
        for animation_url in animations:
            animation_json = requests.get(animation_url).json()
            st_lottie(animation_json)

        if "redirect" in page:
            # Redirect to the main app code
            show_main_app()
    else:
        st.error("Invalid page selection.")


def show_main_app():
    # Upload Excel file
    uploaded_file = st.file_uploader("Upload Data", type="xlsx")

    if uploaded_file is not None:
        # Generate a unique file name
        file_name = f"./uploads/{str(uuid.uuid4())}.xlsx"

        # Save the uploaded file
        with open(file_name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Add the file name to the database
        cursor.execute("INSERT INTO uploaded_files (`filename`) VALUES (%s)", (file_name,))
        myconn.commit()

    # Get list of uploaded files
    uploaded_files = get_uploaded_files()

    # Display list of uploaded files
    if uploaded_files:
        st.subheader("Uploaded Files")
        for file_name in uploaded_files:
            st.write(file_name)

    if uploaded_file is not None:
        file_name = uploaded_file.name

        # Check if the file is already uploaded
        if file_name not in uploaded_files:
            # Save the uploaded file to a specified folder
            file_path = os.path.join("./uploads", file_name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Insert the file name into the database
            query = f"INSERT INTO uploaded_files (file_name) VALUES ('{file_name}')"
            cursor.execute(query)
            myconn.commit()

            # Refresh the list of uploaded files
            uploaded_files = get_uploaded_files()

        # Load data from uploaded Excel file
        df = pd.read_excel(uploaded_file)

        # Department selection
        departments = list(df["Department"].unique())
        department = st.selectbox("Select Department", departments)

        # Check if a department is selected
        if department:
            # Date range selection
            min_date = pd.to_datetime(df["Date"].min()).date()
            max_date = pd.to_datetime(df["Date"].max()).date()
            start_date = st.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
            end_date = st.date_input("End Date", min_value=start_date, max_value=max_date, value=max_date)

            # Get the available KPIs based on column headers
            kpis = list(df.columns[df.columns != "Date"])

            # KPI selection
            selected_kpis = st.multiselect("Select KPIs", kpis)

            # Convert start_date and end_date to datetime objects
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            # Check if the selected KPIs exist in the DataFrame columns
            if all(kpi in df.columns for kpi in selected_kpis):
                # Filter data based on user selection
                mask = (df["Date"].between(start_date, end_date)) & (df["Department"] == department)
                filtered_df = df.loc[mask, ["Date"] + selected_kpis]

                # Check data types of selected KPI columns and convert numeric columns to float
                filtered_df[selected_kpis] = filtered_df[selected_kpis].apply(pd.to_numeric, errors="coerce")

                # Filter out non-numeric columns
                non_numeric_kpis = filtered_df[selected_kpis].select_dtypes(exclude=[np.number]).columns.tolist()
                numeric_kpis = filtered_df[selected_kpis].select_dtypes(include=[np.number]).columns.tolist()

                # Display data in tabular form
                st.subheader("Data")
                st.write(filtered_df[["Date"] + selected_kpis])

                # Generate Excel download link
                st.markdown(generate_excel_download_link(filtered_df), unsafe_allow_html=True)

                # Visualize the filtered data
                if numeric_kpis:
                    st.subheader("Visualizations")

                    # Graph selection
                    selected_graphs = st.multiselect(
                        "Select Graphs",
                        ["Line Chart", "Clustered Bar Chart", "Stacked Bar Chart", "Donut Chart", "Sankey Chart"]
                    )

                    # Line chart for each selected KPI
                    if "Line Chart" in selected_graphs:
                        for kpi in numeric_kpis:
                            line_chart = px.line(filtered_df, x="Date", y=kpi, template="plotly_white")
                            st.plotly_chart(line_chart)

                    # Bar chart (Clustered)
                    if "Clustered Bar Chart" in selected_graphs:
                        clustered_bar_chart = px.bar(filtered_df, x="Date", y=numeric_kpis, template="plotly_white")
                        st.plotly_chart(clustered_bar_chart)

                    # Bar chart (Stacked)
                    if "Stacked Bar Chart" in selected_graphs:
                        stacked_bar_chart = px.bar(
                            filtered_df, x="Date", y=numeric_kpis, template="plotly_white", barmode="stack"
                        )
                        st.plotly_chart(stacked_bar_chart)

                    # Donut chart
                    if "Donut Chart" in selected_graphs:
                        donut_chart_data = filtered_df["Date"].value_counts().reset_index()
                        donut_chart_data.columns = ["KPI", "Participants"]
                        donut_chart = px.pie(donut_chart_data, values="Participants", names="KPI", title="KPI Distribution")
                        donut_chart.update_traces(hole=0.4)
                        st.plotly_chart(donut_chart)

                    # Sankey chart
                    if "Sankey Chart" in selected_graphs:
                        sankey_data = filtered_df.melt(id_vars="Date", value_vars=numeric_kpis)
                        sankey_data.columns = ["Date", "Source", "Value"]
                        sankey_data.dropna(inplace=True)
                        sankey_chart = go.Sankey(
                            node=dict(
                                pad=15,
                                thickness=20,
                                line=dict(color="black", width=0.5),
                                label=numeric_kpis + ["Date"],
                            ),
                            link=dict(
                                source=sankey_data["Date"],
                                target=sankey_data["Source"],
                                value=sankey_data["Value"],
                            ),
                        )
                        sankey_chart.update_layout(title_text="KPI Flow", font_size=10)
                        st.plotly_chart(sankey_chart)
            else:
                st.warning("Please select valid KPIs.")
        else:
            st.warning("Please select a department.")
    else:
        st.warning("Please upload an Excel file.")


if __name__ == "__main__":
    main()


