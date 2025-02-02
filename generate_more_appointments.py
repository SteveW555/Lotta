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

# Swedish first names and last names
first_names = [
    'Erik', 'Lars', 'Karl', 'Anders', 'Johan', 'Per', 'Nils', 'Gustav', 'Mikael',
    'Maria', 'Anna', 'Eva', 'Karin', 'Sara', 'Lisa', 'Lena', 'Helena', 'Sofia',
    'Emma', 'Kristina', 'Björn', 'Magnus', 'Olof', 'Hans', 'Filip'
]

last_names = [
    'Andersson', 'Johansson', 'Karlsson', 'Nilsson', 'Eriksson', 'Larsson',
    'Olsson', 'Persson', 'Svensson', 'Gustafsson', 'Pettersson', 'Bergström',
    'Lindberg', 'Magnusson', 'Lindström', 'Gustavsson', 'Olofsson', 'Lindgren',
    'Berg', 'Nilsson', 'Axelsson', 'Bergman', 'Lundberg', 'Lind', 'Holm'
]

# Uddevalla streets
streets = [
    'Kungsgatan', 'Drottninggatan', 'Norra Drottninggatan', 'Södra Drottninggatan',
    'Västerlånggatan', 'Österlånggatan', 'Norgårdsvägen', 'Strömstadsvägen',
    'Göteborgsvägen', 'Sunningevägen', 'Boxhultsvägen', 'Fasserödsvägen',
    'Kurverödsvägen', 'Sigelhultsvägen', 'Äsperödsvägen', 'Tunnbindaregatan',
    'Kampenhofsgatan', 'Junogatan', 'Margretegärdegatan', 'Bastionsgatan'
]

# Generate 20 unique customers
customers = []
used_names = set()
for _ in range(20):
    while True:
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        if full_name not in used_names:
            used_names.add(full_name)
            street = random.choice(streets)
            house_number = random.randint(1, 99)
            address = f"{street} {house_number}, 451 {random.randint(30, 99)} Uddevalla"
            customers.append((full_name, address))
            break

# Get staff members from existing appointments or use default
if existing_appointments:
    staff = list(set(appt['Staff_name'] for appt in existing_appointments))
else:
    staff = ['Lotta', 'Sara', 'Emma']

# Generate appointments for February and March 2025
start_date = datetime(2025, 2, 1)
end_date = datetime(2025, 3, 31)
all_dates = []
current_date = start_date
while current_date <= end_date:
    if current_date.weekday() < 5:  # Monday to Friday
        all_dates.append(current_date)
    current_date += timedelta(days=1)

# Generate 3-5 appointments for each customer
new_appointments = []
for name, address in customers:
    num_appointments = random.randint(3, 5)
    customer_dates = random.sample(all_dates, num_appointments)
    
    for appointment_date in sorted(customer_dates):
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

# Sort by date and time
df = pd.DataFrame(all_appointments)
df['Appointment_date'] = pd.to_datetime(df['Appointment_date'])
df = df.sort_values(['Appointment_date', 'Start_time'])

# Save to CSV
df.to_csv(appointments_file, index=False)
print(f"Added {len(new_appointments)} new appointments for {len(customers)} new customers")
print(f"Total appointments: {len(all_appointments)}")
