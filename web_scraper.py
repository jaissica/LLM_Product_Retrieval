# for scraping product info - price, EMI and about us
import time
import json
import os
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

driver = webdriver.Chrome()


product_page_url = "https://electronics.sony.com/c/all-headphones"
# product_page_url = "https://electronics.sony.com/audio/soundbars/c/all-soundbars"
# product_page_url = "https://electronics.sony.com/audio/speakers/c/all-speakers"
driver.get(product_page_url)
time.sleep(3)

# Function to extract product name, link, and add to a dictionary
def get_product_data(product_list):
    product_info = {}
    for item in product_list:
        try:
            link_element = item.find('a', href=True)
            product_url = link_element['href'] if link_element else None
            # product_name_tag = item.find('p')
            product_name = item.find('p').text.strip() if item.find('p') else None
            product_id = str(uuid.uuid4())

            if product_url and product_name:
                product_info[product_id] = {
                    'name': product_name,
                    'link': product_page_url + product_url
                }
        except Exception as e:
            print(f"Error occurred while getting product data: {e}")
    return product_info

# Function to extract price, EMI, and About Us
def get_product_details(product_url):
    driver.get(product_url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    product_details = {}

    # Price
    price = fetch_price(soup)
    product_details['price'] = price

    # EMI
    emi = fetch_emi(soup)
    product_details['emi'] = emi

    # About Us
    about_us = fetch_about_us(soup)
    product_details['about_us'] = about_us

    return product_details

# Function to extract price
def fetch_price(soup):
    price_element = soup.find('p', class_='product-pricing__amount')
    if price_element:
        price = price_element.text.strip()
        print(f"Price: {price}")
        return price
    return "Price not found"

# Function to extract EMI statement
def fetch_emi(soup):
    emi_element = soup.find('div', class_='product__affirm__container')
    if emi_element:
        emi_statement = emi_element.text.strip()
        print(f"EMI: {emi_statement}")
        return emi_statement
    return "EMI info not found"

# Function to extract About Us
def fetch_about_us(soup):
    about_us_element = soup.find('div', class_='pdp-summary-highlights__content')
    about_us_info = []
    try:
        see_more_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "pdp-summary-highlights__seeMore"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
        time.sleep(2)
        see_more_button.click()

    except Exception as e:
        print(f"An error occurred while clicking the 'See more' button: {e}")

    if about_us_element:
        about_us_items = about_us_element.find_all('ul', class_="pdp-summary-highlights__content")
        for item in about_us_items:
            about_us_info.append(item.text.strip())
    if about_us_info:
        print(f"About Us: {about_us_info}")
        return about_us_info
    return ["About Us info not found"]

# Function to update product details for all products in the dictionary
def append_product_details(product_dict):
    for product_id, product in product_dict.items():
        product_url = product.get('link')
        product_data = get_product_details(product_url)
        product.update(product_data)

# Scroll to load all products
pause_time = 3
max_attempts = 6
last_height = driver.execute_script("return document.body.scrollHeight")
attempts = 0
while attempts < max_attempts:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        attempts += 1
    else:
        attempts = 0
    last_height = new_height

# For parsing the page content
soup = BeautifulSoup(driver.page_source, 'html.parser')
product_list = soup.find_all('div', class_='custom-product-grid-item__content')

# Extracting list of products and links into a dictionary
products = get_product_data(product_list)

# Updating product details for each product in the dictionary
append_product_details(products)

# Save all product data to a single JSON file
output_file = 'Dataset/products_data_headphones.json'
# output_file = 'Dataset/products_data_soundbars.json'
# output_file = 'Dataset/products_data_speakers.json'
with open(output_file, 'w') as json_file:
    json.dump(products, json_file, indent=4)

print(f"Saved all product data in {output_file}")

driver.quit()


