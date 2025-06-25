import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import calendar

# Database setup
def init_db():
    conn = sqlite3.connect('training_app.db')
    c = conn.cursor()
    # Create training_schedule table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS training_schedule (
            id INTEGER PRIMARY KEY,
            date TEXT,
            activity TEXT,
            miles REAL,
            nutrition_goal_met BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

# Function to add a new training entry
def add_training_entry(date, activity, miles, nutrition_goal_met):
    conn = sqlite3.connect('training_app.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO training_schedule (date, activity, miles, nutrition_goal_met)
        VALUES (?, ?, ?, ?)
    ''', (date, activity, miles, nutrition_goal_met))
    conn.commit()
    conn.close()

# Function to retrieve training entries
def get_training_entries():
    conn = sqlite3.connect('training_app.db')
    df = pd.read_sql_query('SELECT * FROM training_schedule', conn)
    conn.close()
    return df

# Function to delete an entry
def delete_training_entry(entry_id):
    conn = sqlite3.connect('training_app.db')
    c = conn.cursor()
    c.execute('DELETE FROM training_schedule WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Streamlit app layout
st.set_page_config(layout="wide")
st.title("Pittsburg -> DC Training Tracker")

# Sidebar for submission form
with st.sidebar:
    st.header("Submit Training Activity")
    # Input for date
    selected_date = st.date_input("Select Date", datetime.now())
    date_str = selected_date.strftime("%Y-%m-%d")  # Format date as string

    # Input for training activity
    activities = ['S', 'M', 'L', 'XL', 'P', 'A', 'Y', 'R']
    selected_activity = st.selectbox("Select Activity", activities)

    # Miles input for specific activities
    miles = st.number_input("Enter Miles", min_value=0.0, step=0.1)

    # Nutrition goal met checkbox
    nutrition_goal_met = st.checkbox("Nutrition goal met")

    # Button to save entry
    if st.button("Save Entry"):
        add_training_entry(date_str, selected_activity, miles, nutrition_goal_met)
        st.success("Entry saved!")

    st.image("gapco.png")

# Create tabs for the app
tabs = st.tabs(["Goals", "Training Tracker"])

# Goals Tab
with tabs[0]:
    st.header("Goals")
    st.write("**1)** Improve FTP")
    st.write("**2)** Improve body composition")
    st.write("**3)** Complete GAP-CO for female FKT submission")
    
    st.subheader("Monthly Total Mileage")
    st.write("**July:** 700 miles")
    st.write("**August:** 850 miles")
    st.write("**September:** 1000 miles")

    st.header("Ride Definitions")
    st.write("**Short ride:** 10-30 miles, hill repeats, interval sprints, or indoor trainer")
    st.write("**Medium ride:** 31-80 miles, high effort pace")
    st.write("**Long ride:** 81-115 miles, endurance pace")
    st.write("**XL ride:** >115 miles aiming for ~125-150 miles, endurance pace")

    st.header("Weekly Plan")
    
    days = {
        "Monday": {
            "Intensity": "Low-Mid",
            "AM": "Rest or Pete",
            "PM": "Animal Flow or FTP",
            "Total workout time": "0-2 hrs"
        },
        "Tuesday": {
            "Intensity": "High",
            "AM": "Short Ride & Pete",
            "PM": "Yoga",
            "Total workout time": "3-5 hrs"
        },
        "Wednesday": {
            "Intensity": "Mid",
            "AM": "Pete",
            "PM": "Teach Yoga",
            "Total workout time": "2 hrs"
        },
        "Thursday": {
            "Intensity": "High",
            "AM": "Short Ride & Pete",
            "PM": "Teach Yoga x2",
            "Total workout time": "3-6 hrs"
        },
        "Friday": {
            "Intensity": "Low",
            "AM": "Rest or Pete",
            "PM": "Rest",
            "Total workout time": "1-2 hrs"
        },
        "Saturday": {
            "Intensity": "High",
            "AM": "Medium, Large ride, or XL ride",
            "PM": "Rest or Yoga",
            "Total workout time": "4-12 hrs"
        },
        "Sunday": {
            "Intensity": "High",
            "AM": "Medium, Large ride, or XL ride",
            "PM": "Rest or Animal Flow",
            "Total workout time": "4-12 hrs"
        }
    }

    for day, details in days.items():
        st.subheader(day)
        st.write(f"**Intensity:** {details['Intensity']}")
        st.write(f"**AM:** {details['AM']}")
        st.write(f"**PM:** {details['PM']}")
        st.write(f"**Total workout time:** {details['Total workout time']}")
        st.write("---")  # Separator for better readability






# Training Log Tab
with tabs[1]:
    # Main body for weekly calendar
    st.header("Weekly Training Schedule")

    # Get training entries from the database
    training_entries = get_training_entries()
    training_entries['date'] = pd.to_datetime(training_entries['date'])  # Convert 'date' column to datetime

    # Create sections for each day of the week
    if 'date' in training_entries.columns:
        current_month = datetime.now().month
        total_miles = training_entries[training_entries['date'].dt.month == current_month]['miles'].sum()
        st.metric("Total Miles This Month", total_miles)
    
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in week_days:
        st.subheader(day)
        # Get the date for the current day of the week
        today = datetime.now()
        day_date = today + pd.DateOffset(days=(list(calendar.day_name).index(day) - today.weekday()) % 7)

        # Filter entries for the current day
        day_entries = training_entries[training_entries['date'].dt.day_name() == day]

        # Display the entries for the current day
        if not day_entries.empty:
            # Create a new DataFrame with the ID column first
            display_df = day_entries[['id', 'date', 'activity', 'miles', 'nutrition_goal_met']]
            st.dataframe(display_df, use_container_width=True, hide_index=True)  # Hide the index
            
            # Delete functionality
            entry_to_delete = st.selectbox("Select Entry to Delete", 
                                             day_entries['id'].tolist(), 
                                             key=day)
            
            if st.button("Delete Entry", key=f"delete_{day}"):
                delete_training_entry(entry_to_delete)
                st.success("Entry deleted!")
                st.rerun()  # Refresh the app to show the updated entries
        else:
            st.write("No data yet for this day of the week.")

        st.write("---")  # Separator for better readability
