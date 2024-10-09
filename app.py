import csv, time, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

# Function to match CSV headers to form questions
def fill_form_fields(driver, csv_headers, csv_data):
    questions = driver.find_elements(By.XPATH, '//div[contains(@aria-label,"Question")]')
    
    for question in questions:
        label_text = question.text.lower().strip()
        
        # Try to match the question with a CSV header
        for i, header in enumerate(csv_headers):
            if header.lower().strip() in label_text:
                try:
                    input_field = question.find_element(By.XPATH, './/input[@type="text" or @type="number"]')
                    input_field.send_keys(csv_data[i])
                except Exception as e:
                    print(f"Could not fill question: {label_text}, Error: {e}")

# Function to detect and click "Next" or "Submit" button
def click_next_or_submit(driver):
    try:
        next_button = driver.find_element(By.XPATH, '//span[text()="Next"]/parent::button')
        next_button.click()
        print("Clicked 'Next'. Moving to next section.")
    except:
        try:
            submit_button = driver.find_element(By.XPATH, '//span[text()="Submit"]/parent::button')
            submit_button.click()
            print("Clicked 'Submit'. Form submitted.")
        except:
            print("No 'Next' or 'Submit' button found.")

# Function to submit a single form
def submit_form(csv_headers, csv_data, submitted_set):
    # Use webdriver-manager to automatically manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Open the form URL
    form_url = 'https://forms.gle/Qwyjux9XmMwB38Ci9'
    driver.get(form_url)
    
    if csv_data[0] in submitted_set:  # Avoid duplicate submissions
        print(f"Skipping duplicate entry: {csv_data[0]}")
        driver.quit()
        return

    try:
        # Loop through sections of the form
        while True:
            # Fill form fields if questions are found
            fill_form_fields(driver, csv_headers, csv_data)
            
            # Look for the "Next" or "Submit" button and click
            click_next_or_submit(driver)
            
            # Pause to allow the next section to load
            time.sleep(2)
            
            # Check if the form has been submitted (no more sections)
            if "Your response has been recorded" in driver.page_source:
                print(f"Form submitted for {csv_data[0]}.")
                break

        # Record the submission to avoid future duplicates
        save_submitted(csv_data[0])
        
    except Exception as e:
        print(f"Error submitting form for {csv_data[0]}: {e}")
    finally:
        driver.quit()

# Main function to process the CSV and submit forms
def process_csv(file_path):
    submitted_set = load_submitted()
    
    with open(file_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        csv_headers = next(csv_reader)  # Get headers from the first row
        for row in csv_reader:
            submit_form(csv_headers, row, submitted_set)

if __name__ == "__main__":
    # Path to your CSV file with the form data
    csv_file_path = 'student_math_survey.csv'
    
    process_csv(csv_file_path)
