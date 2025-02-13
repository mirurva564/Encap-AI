# this Code will use CSV file, get the leaf name and leaf link,  will do Web Scrapping and perform Chunking.


import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import request 
import json 
import json

# Function to read and print Leaf name and Leaf Link from a CSV file
def print_leaf_data_from_csv(file_path):
    try:
        leaf_data = []
        with open(file_path, mode='r', encoding='utf-8') as file:
            # Create a CSV reader object
            csv_reader = csv.DictReader(file)

            # Loop through each row and store 'Leaf name' and 'Leaf Link'
            for row in csv_reader:
                leaf_name = row.get('Leaf name', 'No Leaf name')  # Default to 'No Leaf name' if not found
                leaf_link = row.get('Leaf Link', 'No Leaf Link')  # Default to 'No Leaf Link' if not found
                print(f"Leaf Name: {leaf_name}, Leaf Link: {leaf_link}")
                
                # Collect the data for scraping
                leaf_data.append((leaf_name, leaf_link))
        
        return leaf_data

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

# Set up headless browser options
chrome_options = Options()
chrome_options.add_argument('--headless')        # Run Chrome in headless mode
chrome_options.add_argument('--no-sandbox')      # Bypass OS security model
chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems

# Initialize the browser
driver = webdriver.Chrome(options=chrome_options)

# Function to scrape text from a given URL
def scrape_text(url):
    try:
        # Navigate to the URL
        driver.get(url)
        # Wait for the page to load
        time.sleep(5)  # Adjust the sleep time if necessary

        # Extract page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Extract text from the specific div by class (Adjust the div class as needed)
        main_content = soup.find('div', {'class': 'ArticleDetailLeftContainer__box'})
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
            return text
        else:
            print(f"Main content not found on {url}")
            return ""

    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        return ""

# Function to chunk the text into smaller pieces
def chunk_text(text, chunk_size=500):
    words = text.split()
    # Break the text into chunks of specified size
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# Function to save chunks to a file
def save_chunks_to_file(data, file_counter):
    file_name = f"scraped_chunks_{file_counter}.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(data)} entries to {file_name}")

# Main function to read CSV, scrape, and chunk data
def scrape_and_chunk(file_path, save_every=100):
    # Step 1: Read the CSV file and get Leaf Name and Leaf Link
    leaf_data = print_leaf_data_from_csv(file_path)

    # Variables to track progress and storage
    chunk_data = []
    row_counter = 0
    file_counter = 1

    # Step 2: Scrape data from each link and chunk it
    for leaf_name, leaf_link in leaf_data:
        if leaf_link and leaf_link != 'No Leaf Link':  # Only scrape if there's a valid link
            print(f"Scraping data from: {leaf_link}")
            scraped_text = scrape_text(leaf_link)

            if scraped_text:
                # Step 3: Chunk the text
                chunks = chunk_text(scraped_text, chunk_size=500)  # Adjust the chunk size if necessary
                print(f"Data for {leaf_name} broken into {len(chunks)} chunks.")
                
                # Store the scraped and chunked data
                chunk_data.append({
                    "leaf_name": leaf_name,
                    "leaf_link": leaf_link,
                    "chunks": chunks
                })

                row_counter += 1

                # Step 4: Save to file after every 100 rows
                if row_counter % save_every == 0:
                    save_chunks_to_file(chunk_data, file_counter)
                    chunk_data = []  # Clear the list after saving
                    file_counter += 1  # Increment file counter

    # Step 5: Save remaining data if any
    if chunk_data:
        save_chunks_to_file(chunk_data, file_counter)

# Call the main function
file_path = 'Zoho KB - Creator.csv'  # Replace with your actual file path
scrape_and_chunk(file_path)

# Close the browser after all scraping
driver.quit()
