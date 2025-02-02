import pandas as pd
import re
import os

# Path to appointments file
data_dir = os.path.join(os.path.dirname(__file__), 'data')
appointments_file = os.path.join(data_dir, 'appointments.csv')

# Read existing appointments
df = pd.read_csv(appointments_file)

# Function to remove postcode from address
def remove_postcode(address):
    # Remove the postcode pattern (e.g., "451 XX" or any 5-6 digit number)
    return re.sub(r',\s*\d{3}\s*\d{2}\s*', ', ', address)

# Print a sample of addresses before change
print("Sample of addresses before change:")
print(df['Address'].head())

# Update addresses
df['Address'] = df['Address'].apply(remove_postcode)

# Save updated appointments
df.to_csv(appointments_file, index=False)

# Print a sample of addresses after change
print("\nSample of addresses after change:")
print(df['Address'].head())
