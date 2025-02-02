import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Create data directory if it doesn't exist
data_dir = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Path to appointments file
appointments_file = os.path.join(data_dir, 'appointments.csv')

# Read existing appointments if file exists
existing_appointments = []
if os.path.exists(appointments_file):
    df = pd.read_csv(appointments_file)
    existing_appointments = df.to_dict('records')
    print(f"Found {len(existing_appointments)} existing appointments")
    
    # Get unique customers from existing appointments
    existing_customers = [(row['Name'], row['Address']) for row in existing_appointments]
    existing_customers = list(set(existing_customers))
    print(f"Found {len(existing_customers)} existing customers")

# Get all weekdays in February 2025
start_date = datetime(2025, 2, 1)
end_date = datetime(2025, 2, 28)
all_dates = []
current_date = start_date
while current_date <= end_date:
    if current_date.weekday() < 5:  # Monday to Friday
        all_dates.append(current_date)
    current_date += timedelta(days=1)

# Get existing staff members or use default ones
if existing_appointments:
    staff = list(set(appt['Staff_name'] for appt in existing_appointments))
else:
    staff = ['Lotta', 'Sara', 'Emma']

# For each existing customer, generate two random appointments
new_appointments = []
for name, address in existing_customers:
    # Get existing appointment dates for this customer to avoid duplicates
    existing_dates = set(
        row['Appointment_date'] 
        for row in existing_appointments 
        if row['Name'] == name
    )
    
    # Filter out dates that already have appointments
    available_dates = [
        d for d in all_dates 
        if d.strftime('%Y-%m-%d') not in existing_dates
    ]
    
    if len(available_dates) >= 2:
        # Randomly select two dates
        customer_dates = random.sample(available_dates, 2)
        
        for appointment_date in customer_dates:
            # Random start time between 8:00 and 15:00
            start_hour = random.randint(8, 15)
            start_time = f"{start_hour:02d}:00"
            end_time = f"{start_hour + 2:02d}:00"
            
            new_appointments.append({
                'Name': name,
                'Address': address,
                'Appointment_date': appointment_date.strftime('%Y-%m-%d'),
                'Start_time': start_time,
                'End_time': end_time,
                'Staff_name': random.choice(staff),
                'Days_since_last_visit': 'First visit'
            })

# Combine existing and new appointments
all_appointments = existing_appointments + new_appointments

# Create DataFrame and save to CSV
df = pd.DataFrame(all_appointments)
df.to_csv(appointments_file, index=False)
print(f"Added {len(new_appointments)} new appointments")
print(f"Total appointments: {len(all_appointments)}")
