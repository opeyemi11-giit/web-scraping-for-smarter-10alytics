# Libraries Used
import csv 
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Step 1 - Configuration and Setup
# Setup Selenium WebDriver
print("Setting up webdriver...")
chrome_option = Options()
chrome_option.add_argument('--headless')
chrome_option.add_argument('--disable-gpu')
chrome_option.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.265 Safari/537.36"
)
print("WebDriver Configuration Done..")

# Install the chrome driver (This is a one time thing)
print("Installing Chrome WD")
service = Service(ChromeDriverManager().install())
print("Final Setup")
driver = webdriver.Chrome(service=service, options=chrome_option)
print("Done")

# Make connection and get URL content
url = "https://www.glasses.com/gl-us/eyeglasses"
print(f"Visting {url} page")
driver.get(url)

# Further instruction to wait for JS to load the files
try:
    print("Waiting for product tiles to load")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'catalog-page'))
    )
    print("Done...Proceed to parse the data")
except (TimeoutError, Exception) as e:
    print(f"Error waiting for {url}: {e}")
    driver.quit()
    print("Closed")

# Data Parsing and Extraction
# Get page source and parse using BeautifulSoup
content = driver.page_source
page = BeautifulSoup(content, 'html.parser')

# Find all products tiles on the page and print the number of products found
product_tiles = page.find_all("a", class_="product-tile")
print(f"Found {len(product_tiles)} products")

products = []

for tile in product_tiles:
    product_info = tile.find('div', class_='product-info') 

    if product_info:
        name_tag = product_info.find('div', class_='product-code') 
        name = name_tag.text if name_tag else "Unknown"

        # brand
        brand_tag = product_info.find('div', class_='product-brand') 
        brand = brand_tag.text if brand_tag else "Unknown"
        
        # price
        price_container = product_info.find('div', class_='product-prices-container') 
        if price_container:
            # former price
            former_price_tag = price_container.find('div', class_='product-list-price') 
            former_price = former_price_tag.text if former_price_tag else 'Unknown'
            # Current price
            current_price_tag = price_container.find('div', class_='product-offer-price') 
            current_price = current_price_tag.text if current_price_tag else 'Unknown'
        else:
            former_price = current_price = "Unknown"
    else:
        brand = name = former_price = current_price = "Unknown"

    data = {
        "Product_Name": name,
        "Brand": brand,
        "Former_Price": former_price,
        "Current_Price": current_price
    }
    print(data)

    # get the product link
    product_link = tile.get('href', '')
    
    # get the discount if available
    discount_tag = tile.find('div', class_='product-badge discount-badge')
    discount = discount_tag.text if discount_tag else None

            
    data = {
        'Brand': brand,
        'Product_Name': name,
        'Former_Price': former_price,
        'Current_Price': current_price,
        'Discount': discount,
        'Product_Link': product_link
    }
    # Append data to the list
    products.append(data)

# Step 3 - Data Storage: store the extracted data in CSV and JSON formats
# Save to CSV file
column_name = products[0].keys() # get the column names
with open('./extracted_data/glassesdotcom.csv', mode='w', newline='', encoding='utf-8') as csv_file: # open up the file with context manager
    dict_writer = csv.DictWriter(csv_file, fieldnames=column_name)
    dict_writer.writeheader()
    dict_writer.writerows(products)
print(f"Saved {len(products)} records to CSV in the extracted data folder.")

# Save to JSON file
with open("./extracted_data/glassesdotcom.json", mode='w') as json_file:
    json.dump(products, json_file, indent=4)
print(f"Saved {len(products)} records to JSON in the extracted data folder.")

# close the browser
driver.quit()
print("End of Web Extraction")

