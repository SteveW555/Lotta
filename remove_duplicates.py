import pandas as pd
import os

# Path to appointments file
data_dir = os.path.join(os.path.dirname(__file__), 'data')
appointments_file = os.path.join(data_dir, 'appointments.csv')

# Read existing appointments
df = pd.read_csv(appointments_file)

print("Before removing duplicates:", len(df))

# Convert Appointment_date to datetime
df['Appointment_date'] = pd.to_datetime(df['Appointment_date'])

# Sort by date and time to keep the latest appointment when removing duplicates
df = df.sort_values(['Appointment_date', 'Start_time'])

# Remove duplicates keeping the last occurrence (latest time) for each customer per day
df['date_only'] = df['Appointment_date'].dt.date
df = df.drop_duplicates(subset=['Name', 'date_only'], keep='last')
df = df.drop('date_only', axis=1)

print("After removing duplicates:", len(df))

# Save the deduplicated appointments
df.to_csv(appointments_file, index=False)

# Print some examples of removed duplicates
print("\nExample rows after deduplication:")
print(df[['Name', 'Appointment_date', 'Start_time', 'End_time']].head())
