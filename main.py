import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from utils.date_helpers import format_appointment_date, calculate_days_since_last_visit
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Define the data file paths
DATA_FILE = os.path.join(DATA_DIR, 'appointments.csv')

# Page configuration
st.set_page_config(
    page_title="Lottas Hemstäd Appointments",
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
if 'form_name' not in st.session_state:
    st.session_state.form_name = ""
if 'form_address' not in st.session_state:
    st.session_state.form_address = ""
if 'last_edited_name' not in st.session_state:
    st.session_state.last_edited_name = None
if 'selected_name' not in st.session_state:
    st.session_state.selected_name = None

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

# Title
st.markdown('<h1 class="hero-title">Lottas Hemstäd Appointments</h1>', unsafe_allow_html=True)
# Main content
appointments_df = load_appointments()

# Sidebar - Add New Appointment
with st.sidebar:
    st.header("Add New Appointment")

    # Get unique customers and their addresses
    if not appointments_df.empty:
        customer_options = ["-New Customer-"] + sorted(appointments_df[['Name', 'Address']].drop_duplicates().apply(
            lambda x: f"{x['Name']} ({x['Address']})", axis=1
        ).tolist())
    else:
        customer_options = ["-New Customer-"]
    
    # Use session state to maintain selection
    if 'selected_customer' not in st.session_state:
        st.session_state.selected_customer = "-New Customer-"
    
    # Ensure selected customer is in options, otherwise reset to "-New Customer-"
    if st.session_state.selected_customer not in customer_options:
        st.session_state.selected_customer = "-New Customer-"
    
    selected_customer = st.selectbox(
        "Select Existing Customer",
        options=customer_options,
        key="customer_selector",
        index=customer_options.index(st.session_state.selected_customer)
    )

    # Update session state
    if selected_customer != st.session_state.selected_customer:
        st.session_state.selected_customer = selected_customer
        # Reset form values when customer changes
        if selected_customer == "-New Customer-":
            st.session_state.form_name = ""
            st.session_state.form_address = ""
        else:
            # Extract name from the selection (remove the address part)
            selected_name = selected_customer.split(" (")[0]
            # Get the customer's details
            customer_details = appointments_df[appointments_df['Name'] == selected_name].iloc[0]
            st.session_state.form_name = customer_details['Name']
            st.session_state.form_address = customer_details['Address']
        st.rerun()

    new_name = st.text_input("Customer Name", value=st.session_state.form_name, key="name_input")
    new_address = st.text_area("Address", value=st.session_state.form_address, key="address_input")
    
    new_date = st.date_input("Appointment Date")
    new_start_time = st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M"), step=1800)
    new_end_time = st.time_input("End Time", value=datetime.strptime("11:00", "%H:%M"), step=1800)
    
    # Updated default staff list
    default_staff = ["Lotta", "Meera", "Alice", "Steve"]
    staff_options = sorted(appointments_df['Staff_name'].unique().tolist()) if not appointments_df.empty else default_staff
    staff_options = sorted(list(set(staff_options + default_staff)))  # Ensure default staff are always included
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

# Display appointments table
if not appointments_df.empty:
    appointments_df['Appointment_date'] = pd.to_datetime(appointments_df['Appointment_date'])
    current_date = pd.to_datetime(datetime.now().date())

    # Sort by date
    appointments_df = appointments_df.sort_values(by='Appointment_date')
    filtered_df = appointments_df

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
    
    # Function to format last visit
    def format_last_visit(x):
        if x == 'First visit':
            return x
        try:
            return f"{int(float(x))} days ago"
        except (ValueError, TypeError):
            return x
    
    display_df['Last Visit'] = display_df['Days_since_last_visit'].apply(format_last_visit)

    # Reorder and rename columns for display
    columns_to_show = ['Date', 'Name', 'Address', 'Time', 'Staff_name', 'Last Visit']
    display_columns = {
        'Staff_name': 'Staff',
        'Last Visit': 'Last Visit'
    }
    
    display_view = display_df[columns_to_show].rename(columns=display_columns)
    display_view = display_view.sort_values(by='Date', ascending=True)
    
    # Configure grid options
    gb = GridOptionsBuilder.from_dataframe(display_view)
    gb.configure_selection(selection_mode='single', use_checkbox=False)
    
    # Pre-select the row if there's a selected name
    if st.session_state.selected_name:
        row_index = display_view[display_view['Name'] == st.session_state.selected_name].index
        if not row_index.empty:
            gb.configure_selection('single', pre_selected_rows=[int(row_index[0])])
    
    # Configure column widths
    gb.configure_column("Date", width=150)
    gb.configure_column("Name", width=150)
    gb.configure_column("Address", width=250)
    gb.configure_column("Time", width=120)
    gb.configure_column("Staff", width=100)
    gb.configure_column("Last Visit", width=100)
    
    gb.configure_grid_options(
        rowStyle={'background-color': '#ffffff'},
        rowHoverStyle={'background-color': '#c8e6c9'},
        rowClass='grid-row'
    )
    gridOptions = gb.build()

    # Display the grid
    grid_response = AgGrid(
        display_view,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        height=400,
        allow_unsafe_jscode=True,
        theme='light',
        key="appointments_grid",
        custom_css={
            ".ag-row-selected": {"background-color": "#a5d6a7 !important"},
            ".ag-row-hover": {"background-color": "#c8e6c9 !important"},
        }
    )

    # Updated handling for selected_rows
    selected_rows = grid_response.get('selected_rows', [])
    
    # Handle selection and update session state
    if isinstance(selected_rows, pd.DataFrame):
        if not selected_rows.empty:
            row = selected_rows.iloc[0]
            st.session_state.selected_customer = row['Name']
    elif isinstance(selected_rows, list) and len(selected_rows) > 0:
        row = selected_rows[0]
        st.session_state.selected_customer = row['Name']
    elif not st.session_state.editing_appointment:  # Only clear if not editing
        st.session_state.selected_customer = None

    # Show detail card only for the selected customer or when editing
    if st.session_state.selected_customer or (isinstance(st.session_state.editing_appointment, pd.Series) and not st.session_state.editing_appointment.empty):
        # Get the customer details
        if isinstance(st.session_state.editing_appointment, pd.Series):
            row = st.session_state.editing_appointment
        else:
            mask = appointments_df['Name'] == st.session_state.selected_customer
            row = appointments_df[mask].iloc[0]
        
        with st.container():
            if not isinstance(st.session_state.editing_appointment, pd.Series):
                # Display mode
                st.markdown(f"### Appointment Details for {row['Name']}")
                st.markdown(f"**Name:** {row['Name']}")
                st.markdown(f"**Address:** {row['Address']}")
                formatted_date = format_date_with_indicator(row['Appointment_date'])
                st.markdown(f"**Date:** {formatted_date}")
                st.markdown(f"**Time:** {row['Start_time']} - {row['End_time']}")
                st.markdown(f"**Staff:** {row['Staff_name']}")
                
                # Format Last Visit
                last_visit = row['Days_since_last_visit']
                if isinstance(last_visit, str):
                    formatted_last_visit = last_visit
                else:
                    formatted_last_visit = f"{int(last_visit)} days ago"
                st.markdown(f"**Last Visit:** {formatted_last_visit}")
                
                st.markdown("---")  # Add a separator line
                
                # Action buttons
                edit_col1, edit_col2 = st.columns([1, 4])
                with edit_col1:
                    if st.button("Edit", key=f"edit_{row['Name'].replace(' ', '_').lower()}"):
                        st.session_state.editing_appointment = row
                        st.session_state.edit_data = {
                            'Name': row['Name'],
                            'Address': row['Address'],
                            'Date': pd.to_datetime(row['Appointment_date']).date() if pd.notna(row['Appointment_date']) else datetime.now().date(),
                            'Start_time': row['Start_time'],
                            'End_time': row['End_time'],
                            'Staff': row['Staff_name']
                        }
                        st.rerun()
                with edit_col2:
                    if st.button("❌ Cancel", key=f"cancel_{row['Name'].replace(' ', '_').lower()}"):
                        # Remove appointment
                        appointments_df = appointments_df[appointments_df['Name'] != row['Name']]
                        save_appointments(appointments_df)
                        st.success("Appointment cancelled successfully!")
                        st.rerun()
            
            else:
                # Edit mode
                st.markdown("### Edit Appointment")
                edit_col1, edit_col2 = st.columns(2)
                
                with edit_col1:
                    new_name = st.text_input("Name", value=st.session_state.edit_data['Name'], key=f"edit_name_{row['Name']}")
                    new_address = st.text_input("Address", value=st.session_state.edit_data['Address'], key=f"edit_addr_{row['Name']}")
                    new_date = st.date_input("Date", value=st.session_state.edit_data['Date'], key=f"edit_date_{row['Name']}")
                
                with edit_col2:
                    new_start_time = st.time_input("Start Time", 
                        value=datetime.strptime(st.session_state.edit_data['Start_time'], "%H:%M").time(),
                        step=1800,  # 30 minutes in seconds
                        key=f"edit_start_{row['Name']}")
                    new_end_time = st.time_input("End Time", 
                        value=datetime.strptime(st.session_state.edit_data['End_time'], "%H:%M").time(),
                        step=1800,  # 30 minutes in seconds
                        key=f"edit_end_{row['Name']}")
                    new_staff = st.selectbox("Staff", 
                        options=staff_options,
                        index=staff_options.index(st.session_state.edit_data['Staff']),
                        key=f"edit_staff_{row['Name']}")
                
                save_col1, save_col2 = st.columns(2)
                with save_col1:
                    if st.button("Save Changes"):
                        # Create a mask for the specific appointment we're editing
                        name_mask = appointments_df['Name'] == row['Name']
                        date_mask = appointments_df['Appointment_date'] == row['Appointment_date']
                        time_mask = appointments_df['Start_time'] == row['Start_time']
                        specific_appointment_mask = name_mask & date_mask & time_mask
                        
                        # Check if we're moving to a date where this customer already has an appointment
                        new_date = pd.to_datetime(new_date)
                        new_date_conflicts = appointments_df[
                            (appointments_df['Name'] == new_name) & 
                            (pd.to_datetime(appointments_df['Appointment_date']).dt.date == new_date.date()) &
                            ~specific_appointment_mask
                        ]
                        
                        # Remove any conflicting appointments
                        if not new_date_conflicts.empty:
                            appointments_df = appointments_df.drop(new_date_conflicts.index)
                        
                        # Update only the specific appointment
                        appointments_df.loc[specific_appointment_mask, 'Name'] = new_name
                        appointments_df.loc[specific_appointment_mask, 'Address'] = new_address
                        appointments_df.loc[specific_appointment_mask, 'Appointment_date'] = new_date
                        appointments_df.loc[specific_appointment_mask, 'Start_time'] = new_start_time.strftime("%H:%M")
                        appointments_df.loc[specific_appointment_mask, 'End_time'] = new_end_time.strftime("%H:%M")
                        appointments_df.loc[specific_appointment_mask, 'Staff_name'] = new_staff
                        
                        # Resort after editing
                        appointments_df = appointments_df.sort_values(by='Appointment_date', ascending=True)
                        
                        save_appointments(appointments_df)
                        st.session_state.editing_appointment = None
                        st.session_state.selected_customer = new_name  # Keep the customer selected
                        st.success("Appointment updated successfully!")
                        st.rerun()
                
                with save_col2:
                    if st.button("Cancel Edit"):
                        st.session_state.editing_appointment = None
                        st.rerun()
            
            if len(display_view) > 1:
                st.markdown("---")
else:
    st.info("No appointments yet. Add your first appointment using the sidebar form.")
