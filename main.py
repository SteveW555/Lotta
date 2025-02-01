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
if 'selected_customer' not in st.session_state:
    st.session_state.selected_customer = None

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

def get_customer_appointments(df, customer_name):
    """Get past, current, and next appointments for a customer"""
    customer_appointments = df[df['Name'] == customer_name].copy()
    customer_appointments['Appointment_date'] = pd.to_datetime(customer_appointments['Appointment_date'])
    current_date = pd.to_datetime(datetime.now().date())

    past_appt = customer_appointments[customer_appointments['Appointment_date'] < current_date].sort_values('Appointment_date', ascending=False).iloc[0] if not customer_appointments[customer_appointments['Appointment_date'] < current_date].empty else None
    current_appt = customer_appointments[customer_appointments['Appointment_date'] == current_date].iloc[0] if not customer_appointments[customer_appointments['Appointment_date'] == current_date].empty else None
    next_appt = customer_appointments[customer_appointments['Appointment_date'] > current_date].sort_values('Appointment_date').iloc[0] if not customer_appointments[customer_appointments['Appointment_date'] > current_date].empty else None

    return past_appt, current_appt, next_appt

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
    show_all = st.checkbox("Show all appointments", value=False)
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
    current_date = pd.to_datetime(datetime.now().date())

    if show_all:
        filtered_df = appointments_df
    else:
        filtered_df = appointments_df[
            appointments_df['Appointment_date'].dt.date == date_filter
        ]

    filtered_df = filtered_df.sort_values(by=sort_by)

    if filtered_df.empty:
        st.info("No appointments found for selected date.")
    else:
        # Format the date and time columns for display
        display_df = filtered_df.copy()
        display_df['Appointment_date'] = display_df['Appointment_date'].apply(format_appointment_date)
        display_df['Time'] = display_df.apply(lambda x: f"{x['Start_time']} - {x['End_time']}", axis=1)
        display_df['Last Visit'] = display_df['Days_since_last_visit'].apply(
            lambda x: f"{x} days ago" if isinstance(x, (int, float)) else x
        )

        # Reorder and rename columns for display
        display_df = display_df[[
            'Name', 'Address', 'Appointment_date', 'Time', 'Staff_name', 'Last Visit'
        ]].rename(columns={
            'Appointment_date': 'Date',
            'Staff_name': 'Staff'
        })

        # Show the dataframe with clickable rows
        selected_row = st.data_editor(
            display_df,
            hide_index=True,
            use_container_width=True,
            key='appointments_table',
            disabled=True
        )

        # Handle row selection
        if st.session_state.appointments_table and len(st.session_state.appointments_table['edited_rows']) > 0:
            selected_index = list(st.session_state.appointments_table['edited_rows'].keys())[0]
            selected_customer = filtered_df.iloc[selected_index]['Name']
            st.session_state.selected_customer = selected_customer

        # Show customer details card if a customer is selected
        if st.session_state.selected_customer:
            st.markdown("### Customer Details")
            past_appt, current_appt, next_appt = get_customer_appointments(appointments_df, st.session_state.selected_customer)

            with st.container():
                st.markdown(f"""
                <div class="customer-details">
                    <h4>{st.session_state.selected_customer}</h4>
                    <hr>
                    <h5>Appointments:</h5>
                    {f"<p><strong>Last Visit:</strong> {format_appointment_date(past_appt['Appointment_date'])} ({past_appt['Start_time']} - {past_appt['End_time']})</p>" if past_appt is not None else ""}
                    {f"<p><strong>Today's Visit:</strong> {format_appointment_date(current_appt['Appointment_date'])} ({current_appt['Start_time']} - {current_appt['End_time']})</p>" if current_appt is not None else ""}
                    {f"<p><strong>Next Visit:</strong> {format_appointment_date(next_appt['Appointment_date'])} ({next_appt['Start_time']} - {next_appt['End_time']})</p>" if next_appt is not None else ""}
                </div>
                """, unsafe_allow_html=True)
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