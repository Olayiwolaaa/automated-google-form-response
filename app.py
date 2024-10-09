import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Define the path to the ChromeDriver
CHROME_DRIVER_PATH = '/path/to/chromedriver'

# Load already submitted records to avoid duplicates
def load_submitted(file='submitted.csv'):
    try:
        with open(file, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

# Save a record of a submitted response
def save_submitted(record, file='submitted.csv'):
    with open(file, 'a') as f:
        f.write(record + '\n')

# Function to submit a single form
def submit_form(data, submitted_set):
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)

    # Open the Google Form URL
    form_url = 'https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform'
    driver.get(form_url)
    
    # Find the form fields and input the data
    try:
        # Assuming the form has three input fields, you will need to modify these to match your form
        form_fields = driver.find_elements(By.XPATH, '//input[@type="text"]')
        
        if data[0] in submitted_set:  # Avoid duplicate submissions
            print(f"Skipping duplicate entry: {data}")
            driver.quit()
            return

        # Fill in the form with the CSV data
        form_fields[0].send_keys(data[0])  # Example: First name
        form_fields[1].send_keys(data[1])  # Example: Last name
        form_fields[2].send_keys(data[2])  # Example: Email

        # Submit the form
        submit_button = driver.find_element(By.XPATH, '//span[text()="Submit"]/parent::button')
        submit_button.click()

        print(f"Form submitted for {data[0]}.")

        # Record the submission to avoid future duplicates
        save_submitted(data[0])

        # Pause for a few seconds to prevent flooding the form with too many requests
        time.sleep(3)
    except Exception as e:
        print(f"Error submitting form for {data[0]}: {e}")
    finally:
        driver.quit()

# Main function to process the CSV and submit forms
def process_csv(file_path):
    submitted_set = load_submitted()
    
    with open(file_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            submit_form(row, submitted_set)

if __name__ == "__main__":
    # Path to your CSV file with the form data
    csv_file_path = 'form_data.csv'
    
    process_csv(csv_file_path)
