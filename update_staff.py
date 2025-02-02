import pandas as pd
import os

# Path to appointments file
data_dir = os.path.join(os.path.dirname(__file__), 'data')
appointments_file = os.path.join(data_dir, 'appointments.csv')

# New staff list
new_staff = ['Lotta', 'Meera', 'Alice', 'Steve']

# Read existing appointments
df = pd.read_csv(appointments_file)

# Count current staff assignments
print("Current staff assignments:")
print(df['Staff_name'].value_counts())

# Randomly reassign staff members while trying to maintain similar workload
import random
from collections import Counter

# Initialize counter for new staff assignments
staff_counter = Counter()

# Update staff names
for idx in df.index:
    # Get staff member with least assignments
    least_assigned = min(new_staff, key=lambda x: staff_counter[x])
    df.at[idx, 'Staff_name'] = least_assigned
    staff_counter[least_assigned] += 1

# Save updated appointments
df.to_csv(appointments_file, index=False)

print("\nNew staff assignments:")
print(df['Staff_name'].value_counts())
