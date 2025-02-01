# Lotta's Appointment Scheduler

A Streamlit-based appointment scheduling system for managing customer appointments.

## Features

- Add and edit appointments
- View appointments in a sortable table
- Highlight today's appointments
- Quick customer selection with auto-fill
- 30-minute time slot increments
- Staff assignment

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SteveW555/Lotta.git
```

2. Install dependencies:
```bash
pip install streamlit pandas
```

3. Run the application:
```bash
streamlit run main.py
```

## Usage

1. **View Appointments**: All appointments are displayed in a sortable table
2. **Add Appointment**: Use the sidebar to add new appointments
   - Select existing customer or add new one
   - Choose date and time
   - Assign staff member
3. **Edit Appointment**: Click the edit button on any appointment to modify details
4. **Cancel Appointment**: Use the cancel button to remove an appointment

## Data Storage

Appointments are stored in a CSV file in the `data` directory.
