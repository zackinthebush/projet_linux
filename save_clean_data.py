import json
from pymongo import MongoClient
import os
from datetime import datetime

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client['financial_data']
collection = db['cac_40_summary']
update_tracker = db['update_tracker']

def process_and_save_data(file_path):
    # Extract date from file name
    # Assuming file name format is 'cac_40_hourly_data_DD-MM-YYYY-HH.json'
    file_name = os.path.basename(file_path)  # Get the file name from the path
    date_str = file_name.replace('cac_40_hourly_data_', '').replace('.json', '')
    # Parse the date string to a datetime object
    file_date = datetime.strptime(date_str, "%d-%m-%Y-%H:%M")

    # Read data from JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Process the data to create a summary
    summary = summarize_data(data)
    # Add file date to the summary
    summary['file_date'] = file_date

    # Save the summary to MongoDB
    collection.insert_one(summary)
    print(f"Summary data saved to MongoDB for {file_name}")

def summarize_data(data):
    """
    Processes the data to create a summary based on the given structure.
    Calculates averages for Open, High, Low, and Close prices.
    """
    metrics = ['Open', 'High', 'Low', 'Close']
    averages = {metric: 0 for metric in metrics}
    total_entries = len(data['Open'])
    
    for metric in metrics:
        metric_values = list(data[metric].values())
        averages[metric] = sum(metric_values) / total_entries if total_entries else 0

    summary = {
        'average_open': averages['Open'],
        'average_high': averages['High'],
        'average_low': averages['Low'],
        'average_close': averages['Close'],
        'total_entries': total_entries
    }
    return summary

def update_last_checked():
    """
    Updates the 'update_tracker' collection with the current timestamp.
    If the collection is empty, it inserts a new document.
    Otherwise, it updates the existing document.
    """
    current_time = datetime.now()
    # Check if the collection already has a document
    if update_tracker.count_documents({}) == 0:
        # If the collection is empty, insert a new document
        update_tracker.insert_one({'timestamp': current_time})
    else:
        # If there's already a document, update it
        update_tracker.update_one({}, {'$set': {'timestamp': current_time}})

    print(f"Update tracker timestamp set to {current_time}")

if __name__ == "__main__":
    folder_path = 'cac_40_data'
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            process_and_save_data(file_path)
            # Delete the file after processing
            os.remove(file_path)
            print(f"Processed and deleted {filename}")
    update_last_checked()
            
            
            

