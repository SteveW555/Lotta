import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from utils.date_helpers import format_appointment_date, calculate_days_since_last_visit

# Page configuration
st.set_page_config(
    page_title="Lotta's Appointments",
    page_icon="📅",
    layout="wide"
)

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'appointments_changed' not in st.session_state:
    st.session_state.appointments_changed = False

# Data file path
DATA_FILE = 'data/appointments.csv'

def load_appointments():
    """Load appointments from CSV file"""
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=[
            'Name', 'Address', 'Appointment_date', 'Start_time',
            'End_time', 'Staff_name', 'Days_since_last_visit'
        ])
    return pd.read_csv(DATA_FILE)

def save_appointments(df):
    """Save appointments to CSV file"""
    os.makedirs('data', exist_ok=True)
    df.to_csv(DATA_FILE, index=False)

# Title
st.markdown('<h1 class="hero-title">Lotta\'s Appointments</h1>', unsafe_allow_html=True)

# Main content
appointments_df = load_appointments()

# Sidebar - Add New Appointment
with st.sidebar:
    st.header("Add New Appointment")
    
    new_name = st.text_input("Customer Name")
    new_address = st.text_area("Address")
    new_date = st.date_input("Appointment Date")
    new_start_time = st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M"))
    new_end_time = st.time_input("End Time", value=datetime.strptime("11:00", "%H:%M"))
    new_staff = st.text_input("Staff Name")
    
    if st.button("Add Appointment"):
        if new_name and new_address and new_staff:
            # Calculate days since last visit
            days_since = calculate_days_since_last_visit(
                appointments_df, new_name, new_date
            )
            
            new_appointment = pd.DataFrame([{
                'Name': new_name,
                'Address': new_address,
                'Appointment_date': new_date,
                'Start_time': new_start_time.strftime("%H:%M"),
                'End_time': new_end_time.strftime("%H:%M"),
                'Staff_name': new_staff,
                'Days_since_last_visit': days_since if days_since is not None else 'First visit'
            }])
            
            appointments_df = pd.concat([appointments_df, new_appointment], ignore_index=True)
            save_appointments(appointments_df)
            st.session_state.appointments_changed = True
            st.success("Appointment added successfully!")

# Main content - View Appointments
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Filter Appointments")
    date_filter = st.date_input("Select Date", value=datetime.now())

with col2:
    st.subheader("Sort By")
    sort_by = st.selectbox(
        "Sort appointments by",
        ['Appointment_date', 'Name', 'Staff_name']
    )

# Filter and sort appointments
if not appointments_df.empty:
    appointments_df['Appointment_date'] = pd.to_datetime(appointments_df['Appointment_date'])
    filtered_df = appointments_df[
        appointments_df['Appointment_date'].dt.date == date_filter
    ]
    
    filtered_df = filtered_df.sort_values(by=sort_by)
    
    if filtered_df.empty:
        st.info("No appointments found for selected date.")
    else:
        for _, appointment in filtered_df.iterrows():
            with st.container():
                st.markdown("""
                    <div class="appointment-card">
                        <h3>{}</h3>
                        <p><strong>Date:</strong> {}</p>
                        <p><strong>Time:</strong> {} - {}</p>
                        <p><strong>Address:</strong> {}</p>
                        <p><strong>Staff:</strong> {}</p>
                        <p><strong>Last Visit:</strong> {}</p>
                    </div>
                """.format(
                    appointment['Name'],
                    format_appointment_date(appointment['Appointment_date']),
                    appointment['Start_time'],
                    appointment['End_time'],
                    appointment['Address'],
                    appointment['Staff_name'],
                    f"{appointment['Days_since_last_visit']} days ago" if isinstance(appointment['Days_since_last_visit'], (int, float)) else appointment['Days_since_last_visit']
                ), unsafe_allow_html=True)
else:
    st.info("No appointments yet. Add your first appointment using the sidebar form.")

# Export functionality
if not appointments_df.empty:
    st.download_button(
        label="Export Appointments (CSV)",
        data=appointments_df.to_csv(index=False).encode('utf-8'),
        file_name='appointments_export.csv',
        mime='text/csv'
    )
