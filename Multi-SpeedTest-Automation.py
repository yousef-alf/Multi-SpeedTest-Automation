import easyocr
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import concurrent.futures
import csv

def extract_download_speed(result, url):
    """Extract download speed from OCR result based on the URL and specific text after certain keywords."""
    download_speed = None
    
    if url == "https://fast.com/":
        # For fast.com, locate the text that comes immediately after 'Mbps'
        for idx, text in enumerate(result):
            if 'Mbps' in text[1]:
                download_speed = result[idx + 1][1] if idx + 1 < len(result) else None
                break
    
    elif url == "https://openspeedtest.com/":
        # For openspeedtest.com, locate the text that comes immediately after 'UPLOAD'
        for idx, text in enumerate(result):
            if 'UPLOAD' in text[1]:
                download_speed = result[idx + 1][1] if idx + 1 < len(result) else None
                break

    elif url == "https://speed.measurementlab.net/":
        # For speed.measurementlab.net, locate the text that comes immediately after 'Download'
        for idx, text in enumerate(result):
            if 'Download' in text[1]:
                download_speed = result[idx + 1][1] if idx + 1 < len(result) else None
                break

    elif url == "https://speedsmart.net/":
        # For speedsmart.net, locate the text that comes 4 keys after 'ALL FINISHED'
        for idx, text in enumerate(result):
            if 'ALL FINISHED' in text[1]:
                download_speed = result[idx + 4][1] if idx + 4 < len(result) else None
                break

    elif url == "https://www.speedtest.net/":
        # For speedtest.net, locate the text that comes immediately after 'UPLOAD Mbps'
        for idx, text in enumerate(result):
            if 'with a' in text[1]:
                download_speed = result[idx + 1][1] if idx + 1 < len(result) else None
                break
    
    return download_speed

def run_test(driver, url, action, wait_time, test_number, download_speeds, all_texts):
    """Function to visit a URL, interact with it, and return result."""
    try:
        # Open the URL
        driver.get(url)
        
        # Wait for the specified time
        time.sleep(wait_time)
        
        # Perform actions based on the site
        if action == "show_more_info" and url == "https://fast.com/":
            try:
                # Wait for the 'Show More Info' button to be clickable
                show_more_button = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.ID, "show-more-details-link"))
                )
                show_more_button.click()
                print(f"Clicked 'Show More Info' on {url}")
            except Exception as e:
                print(f"Error on {url} while trying to click 'Show More Info': {e}")
        
        elif action == "go_button" and url == "https://www.speedtest.net/":
            try:
                # Wait for the 'Go' button and click it
                go_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "start-text"))
                )
                go_button.click()
                print(f"Clicked 'Go' button on {url}")
            except Exception as e:
                print(f"Error on {url} while trying to click 'Go' button: {e}")
        
        elif action == "agree_and_begin" and url == "https://speed.measurementlab.net/":
            try:
                # Use JavaScript to check the checkbox directly
                driver.execute_script("document.getElementById('demo-human').checked = true;")
                
                # Trigger both 'click' and 'change' events to ensure JavaScript reacts
                driver.execute_script("document.getElementById('demo-human').dispatchEvent(new Event('click'));")
                driver.execute_script("document.getElementById('demo-human').dispatchEvent(new Event('change'));")
                
                # Wait for AngularJS to update the button's state
                WebDriverWait(driver, 20).until(
                    lambda driver: driver.execute_script('return !angular.element(document.querySelector("a.startButton")).hasClass("disabled")')
                )
                
                # Find the "BEGIN" button again after AngularJS updates the state
                begin_button = driver.find_element(By.XPATH, '//a[contains(@class, "startButton") and not(contains(@class, "disabled"))]')
                driver.execute_script("arguments[0].click();", begin_button)
                print(f"Clicked 'I agree' and 'BEGIN' button on {url}")
            
            except Exception as e:
                print(f"Error on {url} while trying to agree and click 'BEGIN' button: {e}")
        
        elif action == "start_test" and url == "https://speedsmart.net/":
            try:
                # Define the XPath for the 'Start Test' button
                start_button_xpath = "//button[@id='start_button' and contains(text(), 'Start Test')]"
                
                # Wait for the 'Start Test' button to be visible and clickable
                WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, start_button_xpath)))
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, start_button_xpath)))
                start_button = driver.find_element(By.XPATH, start_button_xpath)
                driver.execute_script("arguments[0].click();", start_button)
                print(f"Clicked 'Start Test' button on {url}")
                
            except Exception as e:
                print(f"Error on {url} while trying to click 'Start Test' button: {e}")

        elif action == "start_test_openspeedtest" and url == "https://openspeedtest.com/":
            try:
                # Press 'Enter' after the page has loaded
                time.sleep(5)  # Wait a moment to ensure the page is fully loaded
                body = driver.find_element(By.TAG_NAME, 'body')
                body.send_keys(Keys.RETURN)  # Send Enter key
                print(f"Pressed 'Enter' on OpenSpeedTest at {url}")
            except Exception as e:
                print(f"Error on {url} while trying to press 'Enter' on OpenSpeedTest: {e}")
        
        # Increase the time before taking the screenshot
        time.sleep(120)  # Increase this time as per your requirement (in seconds)
        
        # Take a screenshot of the current page
        screenshot_filename = f"screenshot_{url.split('//')[1].replace('/', '_')}.png"
        driver.save_screenshot(screenshot_filename)
        print(f"Screenshot saved for {url} as {screenshot_filename}")

        # OCR: Extract text from the screenshot (with retries)
        reader = easyocr.Reader(['en'])

        # Retry OCR with a delay to allow more time for reading
        def ocr_retry_attempts(filename, retries=3, delay=5):
            for attempt in range(retries):
                result = reader.readtext(filename)
                if result:  # If OCR found text, break the loop
                    return result
                print(f"OCR attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            return []  # Return empty list if OCR fails after retries

        result = ocr_retry_attempts(screenshot_filename)

        # Collect all readable text in a dictionary with separate keys for each text
        ocr_text_dict = {}
        for idx, text in enumerate(result, start=1):
            ocr_text_dict[f"text_{idx}"] = text[1]  # Storing each OCR text as a separate key-value pair

        # Add OCR text dictionary to all_texts with test_number and URL as key
        all_texts[test_number] = {
            "URL": url,
            "Test Number": test_number,
            **ocr_text_dict  # Unpack the OCR text dictionary to add all the text entries as separate keys
        }

        # Extract download speed based on the URL and the specified keywords
        download_speed = extract_download_speed(result, url)
        
        # Store the result in the list with the test number
        if download_speed:
            download_speeds.append((test_number, download_speed))
            print(f"Test {test_number} - Download Speed: {download_speed}")
        else:
            print(f"Test {test_number} - Download Speed not found.")
        
    except Exception as e:
        print("An error occurred:", e)
        print("Current page URL:", driver.current_url)
        print("Page source snippet:", driver.page_source[:2000])  # Print first 2000 characters of page source for debugging


def main():
    """Run the tests sequentially with a 10-second delay after each starts."""
    urls = [
        {"url": "https://fast.com/", "wait_time": 40, "action": "show_more_info"},
        {"url": "https://www.speedtest.net/", "wait_time": 20, "action": "go_button"},
        {"url": "https://speed.measurementlab.net/", "wait_time": 20, "action": "agree_and_begin"},
        {"url": "https://speedsmart.net/", "wait_time": 20, "action": "start_test"},
        {"url": "https://openspeedtest.com/", "wait_time": 20, "action": "start_test_openspeedtest"}
    ]

    # List to store the download speeds with their respective test numbers
    download_speeds = []
    # Dictionary to store all the OCR extracted text
    all_texts = {}

    # Using ThreadPoolExecutor to run all tests sequentially in separate windows
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        test_number = 1
        for entry in urls:
            # Create a new driver instance for each test
            driver_instance = webdriver.Chrome()
            futures.append(executor.submit(run_test, driver_instance, entry["url"], entry["action"], entry["wait_time"], test_number, download_speeds, all_texts))

            # Wait for 10 seconds before starting the next test
            time.sleep(10)
            test_number += 1

        # Wait for all futures to complete
        for future in concurrent.futures.as_completed(futures):
            future.result()  # To re-raise any exceptions that occurred in the threads)

    # Write all the OCR text to a CSV file
    csv_filename = "ocr_texts.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header = ["Test Number", "URL"]  # Starting with the Test Number and URL as base columns
        # Add OCR text columns dynamically
        for i in range(1, len(all_texts) + 1):
            header.append(f"text_{i}")
        writer.writerow(header)  # Write header row

        for test_number, data in all_texts.items():
            row = [data["Test Number"], data["URL"]]
            # Add all text values dynamically for the current row
            for i in range(1, len(data) - 2 + 1):  # Skipping Test Number and URL columns
                row.append(data[f"text_{i}"])
            writer.writerow(row)

    # Write all the collected download speeds to a CSV file
    csv_filename_speeds = "all_speedtests.csv"
    with open(csv_filename_speeds, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Test Number", "Download Speed"])  # Write header row
        for test_number, download_speed in download_speeds:
            writer.writerow([test_number, download_speed])  # Write each test number and download speed

    print(f"All tests completed. Results saved to {csv_filename} and {csv_filename_speeds}")

# Run the function
main()
