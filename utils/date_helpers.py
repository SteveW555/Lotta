from datetime import datetime
import pandas as pd

def format_appointment_date(date_obj):
    """Convert date object to 'Thursday dd-mm' format"""
    try:
        if pd.isna(date_obj):
            return "No date"
        return pd.to_datetime(date_obj).strftime("%A %d-%m")
    except:
        return "Invalid date"

def calculate_days_since_last_visit(appointments_df, customer_name, current_date):
    """Calculate days since last visit for a customer"""
    if appointments_df.empty:
        return None
    
    customer_appointments = appointments_df[appointments_df['Name'] == customer_name]
    if customer_appointments.empty:
        return None
    
    # Convert dates to datetime
    customer_appointments['Appointment_date'] = pd.to_datetime(customer_appointments['Appointment_date'])
    current_date = pd.to_datetime(current_date)
    
    # Get the most recent past appointment
    past_appointments = customer_appointments[
        customer_appointments['Appointment_date'] < current_date
    ].sort_values('Appointment_date', ascending=False)
    
    if past_appointments.empty:
        return None
    
    last_visit = past_appointments.iloc[0]['Appointment_date']
    days_since = (current_date - last_visit).days
    return days_since
