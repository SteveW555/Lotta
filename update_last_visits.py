import pandas as pd
import random
import os

# Path to appointments file
data_dir = os.path.join(os.path.dirname(__file__), 'data')
appointments_file = os.path.join(data_dir, 'appointments.csv')

# Read existing appointments
df = pd.read_csv(appointments_file)

# Count current 'First Visit' entries
first_visits = df['Days_since_last_visit'] == 'First visit'
print(f"Found {first_visits.sum()} 'First visit' entries")

# Keep some first visits (about 20% of them)
first_visit_indices = df[first_visits].index.tolist()
keep_first_visits = random.sample(first_visit_indices, k=int(len(first_visit_indices) * 0.2))

# Update the rest with random days
for idx in first_visit_indices:
    if idx not in keep_first_visits:
        df.at[idx, 'Days_since_last_visit'] = random.randint(1, 40)

# Save updated appointments
df.to_csv(appointments_file, index=False)

# Print summary
print("\nAfter updates:")
print("First visits remaining:", len(df[df['Days_since_last_visit'] == 'First visit']))
print("\nSample of updated entries:")
print(df[['Name', 'Days_since_last_visit']].sample(5))
