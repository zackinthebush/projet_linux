import yfinance as yf
import json
from datetime import datetime

def fetch_and_save_cac40_data():
    # Fetch data for the CAC 40
    cac_40 = yf.Ticker("^FCHI")

    # Get historical data for the past hour
    # Note: This attempts to fetch the most recent data within the last day with an hourly interval
    hist_data = cac_40.history(period="1d", interval="1h")

    # Convert the DataFrame to a JSON format
    json_data = hist_data.to_json()

    # Get the current date and time
    now = datetime.now()
    # Format the date and time in the desired format (day-month-year-hour)
    formatted_date = now.strftime("%d-%m-%Y-%H:%M")

    # Specify the file path with the formatted date and time in the name
    file_path = f'cac_40_data/cac_40_hourly_data_{formatted_date}.json'

    # Save the data to a JSON file
    with open(file_path, 'w') as file:
        file.write(json_data)

    print(f"Data saved to {file_path}")

# Call the function to fetch and save CAC 40 data
fetch_and_save_cac40_data()

