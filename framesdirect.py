## Importing Libraries
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

print("Configuring Webdriver...")
chrome_opt = Options() # initialize the chrome webdriver 
chrome_opt.add_argument("--headless=new") # run in headless mode (new syntax for Chrome 109+)
chrome_opt.add_argument("--disable-gpu") # disable gpu acceleration
chrome_opt.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36") # set user agent to avoid detection
print("Configuration done!")

# Setting up the webdriver: Installation and Initialization
print("Installing Chrome Webdriver...")
service = Service(ChromeDriverManager().install())
print("Final Setup")
driver = webdriver.Chrome(service=service, options=chrome_opt)
print("done!!")

URL = "https://www.framesdirect.com/eyeglasses"

print(f"Visiting {URL} page")
driver.get(URL)

# Further Instrauctions and Waits
try:
    print("Waiting for the page to load...")
    WDW(driver, 10).until(EC.presence_of_element_located((By.
    CLASS_NAME, "fd-cat")))
    print("Done, Proceed!.")
except Exception as e:
    print(f"Error occurred while waiting for the page to load: {e}")
    pass

content = driver.page_source
page = BeautifulSoup(content, 'html.parser')

print(content) 

print(page)

# prod_holder = page.find_all('div', class_="prod-holder")
# print(f"Found {len(prod_holder)} products on the page.")

prod_holder = page.find_all('div', class_="prod-holder")
# Filter to only actual products (exclude ads)
prod_holder = [p for p in prod_holder if p.get('data-element-id', '').startswith('Tiles_Tile')]
print(f"Found {len(prod_holder)} products on the page.")



product = []

for prod in prod_holder:
    product_title = prod.find('div', class_="prod-title")
    prod_bot = prod.find('div', class_="prod-bot")

    if product_title:
        # brand_name
        brand_name = product_title.find('div', class_="catalog-name")
        brand = brand_name.text if brand_name else "Unknown"

        # product_name
        product_name = product_title.find('div', class_="product_name")
        name = product_name.text if product_name else "Unknown"

        # prices
      

        if prod_bot:
            # current_price
            current_price_tag = prod_bot.find('div', class_="prod-aslowas")
            current_price = current_price_tag.text if current_price_tag else "Unknown"
            # former_price
            former_price_tag = prod_bot.find('div', class_="prod-catalog-retail-price")
            former_price = former_price_tag.text if former_price_tag else "Unknown"
            
        else:
            current_price = former_price = "Unknown"
    else:
        brand = name = current_price = former_price = "Unknown"
    data = {
        "brand": brand,
        "name": name,
        "current_price": current_price,
        "former_price": former_price
    }
    print(data)
    # Append the data to the list
    product.append(data)

    # Step 3 - Data Storage: store the extracted data in CSV and JSON formats
# save to csv file
with open('framesdirect_products.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=["brand", "name", "current_price", "former_price"])
    writer.writeheader()
    writer.writerows(product)  
print("Data saved to framesdirect_products.csv")

# save to json file
with open('framesdirect_products.json', 'w') as json_file:
    json.dump(product, json_file, indent=4)
print("Data saved to framesdirect_products.json")

# close the browser
driver.quit()
print("End of Web Extraction")

