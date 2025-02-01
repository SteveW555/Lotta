import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from utils.date_helpers import format_appointment_date, calculate_days_since_last_visit

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Define the data file path
DATA_FILE = os.path.join(DATA_DIR, 'appointments.csv')

# Page configuration
st.set_page_config(
    page_title="Lotta's Appointments",
    page_icon="📅",
    layout="wide"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), 'styles', 'custom.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'appointments_changed' not in st.session_state:
    st.session_state.appointments_changed = False
if 'appointments_df' not in st.session_state:
    st.session_state.appointments_df = None
if 'selected_customer' not in st.session_state:
    st.session_state.selected_customer = None
if 'selected_row' not in st.session_state:
    st.session_state.selected_row = None
if 'editing_appointment' not in st.session_state:
    st.session_state.editing_appointment = None
if 'edit_data' not in st.session_state:
    st.session_state.edit_data = {
        'Name': '',
        'Address': '',
        'Date': datetime.now().date(),
        'Start_time': '09:00',
        'End_time': '10:00',
        'Staff': ''
    }

def load_appointments():
    """Load appointments from CSV file or session state"""
    if st.session_state.appointments_df is not None:
        return st.session_state.appointments_df
        
    if not os.path.exists(DATA_FILE):
        # Create an empty DataFrame with the correct columns
        df = pd.DataFrame(columns=[
            'Name', 'Address', 'Appointment_date', 'Start_time',
            'End_time', 'Staff_name', 'Days_since_last_visit'
        ])
    else:
        df = pd.read_csv(DATA_FILE)
        # Convert date columns
        df['Appointment_date'] = pd.to_datetime(df['Appointment_date'])
    
    st.session_state.appointments_df = df
    return df

def save_appointments(df):
    """Save appointments to session state and offer download"""
    st.session_state.appointments_df = df
    st.session_state.appointments_changed = True
    
    # If changes were made, show download button
    if st.session_state.appointments_changed:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download appointments data",
            data=csv,
            file_name="appointments.csv",
            mime="text/csv"
        )

def get_customer_appointments(df, customer_name):
    """Get past, current, and next appointments for a customer"""
    customer_appointments = df[df['Name'] == customer_name].copy()
    customer_appointments['Appointment_date'] = pd.to_datetime(customer_appointments['Appointment_date'])
    current_date = pd.to_datetime(datetime.now().date())

    past_appt = customer_appointments[customer_appointments['Appointment_date'] < current_date].sort_values('Appointment_date', ascending=False).iloc[0] if not customer_appointments[customer_appointments['Appointment_date'] < current_date].empty else None
    current_appt = customer_appointments[customer_appointments['Appointment_date'] == current_date].iloc[0] if not customer_appointments[customer_appointments['Appointment_date'] == current_date].empty else None
    next_appt = customer_appointments[customer_appointments['Appointment_date'] > current_date].sort_values('Appointment_date').iloc[0] if not customer_appointments[customer_appointments['Appointment_date'] > current_date].empty else None

    return past_appt, current_appt, next_appt

def format_appointment_date(date):
    """Format the appointment date"""
    if pd.isna(date):
        return ''
    return date.strftime("%Y-%m-%d")  # Changed to YYYY-MM-DD format for proper sorting

# Title
st.markdown('<h1 class="hero-title">Lotta\'s Appointments</h1>', unsafe_allow_html=True)

# Main content
appointments_df = load_appointments()

# Sidebar - Add New Appointment
with st.sidebar:
    st.header("Add New Appointment")

    # Add appointment form
    st.markdown("### Add New Appointment")
    
    # Get unique customers and their addresses
    if not appointments_df.empty:
        customer_options = ["-New Customer-"] + sorted(appointments_df[['Name', 'Address']].drop_duplicates().apply(
            lambda x: f"{x['Name']} ({x['Address']})", axis=1
        ).tolist())
    else:
        customer_options = ["-New Customer-"]
    
    selected_customer = st.selectbox("Select Existing Customer", options=customer_options, key="customer_selector")
    
    # Initialize default values
    default_name = ""
    default_address = ""
    
    # If a customer is selected, get their details
    if selected_customer != "-New Customer-":
        # Extract name from the selection (remove the address part)
        selected_name = selected_customer.split(" (")[0]
        # Get the customer's details
        customer_details = appointments_df[appointments_df['Name'] == selected_name].iloc[0]
        default_name = customer_details['Name']
        default_address = customer_details['Address']
    
    new_name = st.text_input("Customer Name", value=default_name)
    new_address = st.text_area("Address", value=default_address)
    new_date = st.date_input("Appointment Date")
    new_start_time = st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M"), step=1800)
    new_end_time = st.time_input("End Time", value=datetime.strptime("11:00", "%H:%M"), step=1800)
    staff_options = sorted(appointments_df['Staff_name'].unique().tolist())
    new_staff = st.selectbox("Staff", options=staff_options, index=0)

    if st.button("Add Appointment"):
        if new_name and new_address and new_staff:
            days_since = calculate_days_since_last_visit(
                appointments_df, new_name, new_date
            )

            new_appointment = pd.DataFrame([{
                'Name': new_name,
                'Address': new_address,
                'Appointment_date': pd.Timestamp(new_date),
                'Start_time': new_start_time.strftime("%H:%M"),
                'End_time': new_end_time.strftime("%H:%M"),
                'Staff_name': new_staff,
                'Days_since_last_visit': days_since if days_since is not None else 'First visit'
            }])
            
            appointments_df = pd.concat([appointments_df, new_appointment], ignore_index=True)
            appointments_df = appointments_df.sort_values(by='Appointment_date', ascending=True)
            
            save_appointments(appointments_df)
            st.success("Appointment added successfully!")
            st.rerun()

# Add file upload option in sidebar
with st.sidebar:
    st.write("### Data Management")
    uploaded_file = st.file_uploader("Upload appointments data", type="csv")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df['Appointment_date'] = pd.to_datetime(df['Appointment_date'])
            st.session_state.appointments_df = df
            st.success("Data uploaded successfully!")
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")

# Main content - View Appointments
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Filter Appointments")
    show_all = st.checkbox("Show all appointments", value=True)
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

    # Default sort by date
    appointments_df = appointments_df.sort_values(by='Appointment_date')

    if show_all:
        filtered_df = appointments_df
    else:
        # Show appointments within 3 days before and after the selected date
        date_filter_dt = pd.to_datetime(date_filter)
        date_range_start = date_filter_dt - timedelta(days=3)
        date_range_end = date_filter_dt + timedelta(days=3)

        filtered_df = appointments_df[
            (appointments_df['Appointment_date'] >= date_range_start) &
            (appointments_df['Appointment_date'] <= date_range_end)
        ]

    # Apply sorting if specified
    if sort_by != 'Appointment_date':
        filtered_df = filtered_df.sort_values(by=sort_by)

    if filtered_df.empty:
        st.info("No appointments found for selected date range.")
    else:
        # Get unique staff members
        staff_options = sorted(filtered_df['Staff_name'].unique().tolist())
        
        # Format the date and time columns for display
        display_df = filtered_df.copy()
        # Keep both raw and formatted dates
        display_df['raw_date'] = display_df['Appointment_date']
        
        # First sort by date
        display_df = display_df.sort_values(by='Appointment_date', ascending=True)
        
        # Then format the date for display with NaT handling
        def format_date_with_indicator(x):
            if pd.isna(x):
                return ''
            # Format as YYYY-MM-DD Day for proper sorting, but show day name for readability
            date_str = x.strftime('%Y-%m-%d %A')
            return f" {date_str}" if x.date() == current_date.date() else date_str
        
        display_df['Date'] = display_df['Appointment_date'].apply(format_date_with_indicator)
        display_df['Time'] = display_df.apply(lambda x: f"{x['Start_time']} - {x['End_time']}", axis=1)
        display_df['Last Visit'] = display_df['Days_since_last_visit'].apply(
            lambda x: f"{x} days ago" if isinstance(x, (int, float)) else x
        )

        # Reorder and rename columns for display
        columns_to_show = ['Name', 'Address', 'Date', 'Time', 'Staff_name', 'Last Visit']
        display_columns = {
            'Staff_name': 'Staff',
            'Last Visit': 'Last Visit'  # Ensure column name matches
        }
        
        # Create a copy with only display columns and sort by date
        display_view = display_df[columns_to_show].rename(columns=display_columns)
        display_view = display_view.sort_values(by='Date', ascending=True)
        
        # Add selection column
        if 'selected' not in display_view.columns:
            display_view.insert(0, 'selected', False)

        # Add the selection column
        edited_df = st.data_editor(
            display_view,
            column_config={
                "selected": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select appointment",
                    default=False,
                    width="small"
                ),
                "Name": st.column_config.Column(
                    "Name",
                    width=136
                ),
                "Address": st.column_config.Column(
                    "Address",
                    width=144
                ),
                "Date": st.column_config.Column(
                    "Date",
                    width=150
                ),
                "Time": st.column_config.Column(
                    "Time",
                    width=105
                ),
                "Staff": st.column_config.Column(
                    "Staff",
                    width=70
                ),
                "Last Visit": st.column_config.Column(
                    "Last Visit",
                    width=85,
                    help="Days since customer's last visit"
                )
            },
            height=400,
            key="appointment_table",
            disabled=["Name", "Address", "Date", "Time", "Staff", "Last Visit"],
            column_order=["selected", "Name", "Address", "Date", "Time", "Staff", "Last Visit"],
            use_container_width=True
        )

        # Show detail card for selected rows
        selected_rows = edited_df[edited_df['selected']]
        if not selected_rows.empty:
            for _, row in selected_rows.iterrows():
                # Get the full row data including raw_date
                full_row_data = display_df[display_df['Name'] == row['Name']].iloc[0]
                
                with st.container():
                    st.markdown(f"### Appointment Details for {row['Name']}")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Customer Name:** {row['Name']}")
                        st.markdown(f"**Address:** {row['Address']}")
                        st.markdown(f"**Date:** {row['Date']}")
                    
                    with col2:
                        st.markdown(f"**Time:** {row['Time']}")
                        st.markdown(f"**Staff:** {row['Staff']}")
                        st.markdown(f"**Last Visit:** {row['Last Visit']}")

                    st.markdown("---")  # Add a separator line

                    # Action buttons in a cleaner layout
                    button_col1, button_col2, button_col3 = st.columns(3)
                    
                    with button_col1:
                        if st.session_state.editing_appointment != row['Name'].replace(" ", "_").lower():
                            if st.button("", key=f"edit_{row['Name'].replace(' ', '_').lower()}"):
                                st.session_state.editing_appointment = row['Name'].replace(" ", "_").lower()
                                # Split time range into start and end times
                                time_parts = row['Time'].split(' - ')
                                start_time = time_parts[0] if len(time_parts) > 0 else "09:00"
                                end_time = time_parts[1] if len(time_parts) > 1 else "10:00"

                                st.session_state.edit_data = {
                                    'Name': full_row_data['Name'],
                                    'Address': full_row_data['Address'],
                                    'Date': full_row_data['raw_date'].date() if pd.notna(full_row_data['raw_date']) else datetime.now().date(),
                                    'Start_time': start_time,
                                    'End_time': end_time,
                                    'Staff': full_row_data['Staff_name']
                                }
                                st.rerun()
                        else:
                            # Show edit form
                            st.markdown("### Edit Appointment")
                            edit_col1, edit_col2 = st.columns(2)
                            
                            with edit_col1:
                                new_name = st.text_input("Name", value=st.session_state.edit_data['Name'], key=f"edit_name_{row['Name'].replace(' ', '_').lower()}")
                                new_address = st.text_input("Address", value=st.session_state.edit_data['Address'], key=f"edit_address_{row['Name'].replace(' ', '_').lower()}")
                                new_date = st.date_input("Date", value=st.session_state.edit_data['Date'], key=f"edit_date_{row['Name'].replace(' ', '_').lower()}")
                            
                            with edit_col2:
                                new_start_time = st.time_input("Start Time", 
                                    value=datetime.strptime(st.session_state.edit_data['Start_time'], "%H:%M").time() if isinstance(st.session_state.edit_data['Start_time'], str) else st.session_state.edit_data['Start_time'],
                                    key=f"edit_start_{row['Name'].replace(' ', '_').lower()}",
                                    step=1800)  # 30 minutes in seconds
                                new_end_time = st.time_input("End Time", 
                                    value=datetime.strptime(st.session_state.edit_data['End_time'], "%H:%M").time() if isinstance(st.session_state.edit_data['End_time'], str) else st.session_state.edit_data['End_time'],
                                    key=f"edit_end_{row['Name'].replace(' ', '_').lower()}",
                                    step=1800)  # 30 minutes in seconds
                                new_staff = st.selectbox("Staff", 
                                    options=staff_options,
                                    index=staff_options.index(st.session_state.edit_data['Staff']) if st.session_state.edit_data['Staff'] in staff_options else 0,
                                    key=f"edit_staff_{row['Name'].replace(' ', '_').lower()}")
                            
                            save_col1, save_col2 = st.columns(2)
                            with save_col1:
                                if st.button("Save Changes", key=f"save_{row['Name'].replace(' ', '_').lower()}"):
                                    # Update the appointment in the dataframe
                                    mask = appointments_df['Name'] == row['Name']
                                    appointments_df.loc[mask, 'Name'] = new_name
                                    appointments_df.loc[mask, 'Address'] = new_address
                                    appointments_df.loc[mask, 'Appointment_date'] = pd.Timestamp(new_date)
                                    appointments_df.loc[mask, 'Start_time'] = new_start_time.strftime("%H:%M")
                                    appointments_df.loc[mask, 'End_time'] = new_end_time.strftime("%H:%M")
                                    appointments_df.loc[mask, 'Staff_name'] = new_staff
                                    
                                    # Resort after editing
                                    appointments_df = appointments_df.sort_values(by='Appointment_date', ascending=True)
                                    
                                    save_appointments(appointments_df)
                                    st.session_state.editing_appointment = None
                                    st.success("Appointment updated successfully!")
                                    st.rerun()
                            
                            with save_col2:
                                if st.button("Cancel Edit", key=f"cancel_edit_{row['Name'].replace(' ', '_').lower()}"):
                                    st.session_state.editing_appointment = None
                                    st.rerun()
                    
                    with button_col2:
                        if st.session_state.editing_appointment != row['Name'].replace(" ", "_").lower():
                            if st.button("", key=f"cancel_{row['Name'].replace(' ', '_').lower()}"):
                                appointments_df = appointments_df[appointments_df['Name'] != row['Name']]
                                save_appointments(appointments_df)
                                st.success("Appointment cancelled successfully!")
                                st.rerun()
                    
                    with button_col3:
                        if st.session_state.editing_appointment != row['Name'].replace(" ", "_").lower():
                            if st.button("", key=f"note_{row['Name'].replace(' ', '_').lower()}"):
                                st.text_area("Add a note for this appointment", key=f"note_text_{row['Name'].replace(' ', '_').lower()}")
                    
                    if len(selected_rows) > 1:
                        st.markdown("---")
else:
    st.info("No appointments yet. Add your first appointment using the sidebar form.")