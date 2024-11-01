# for scraping features
import time
import json
import os
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

driver = webdriver.Chrome()

url = "https://electronics.sony.com/c/all-headphones"
driver.get(url)
time.sleep(3)

# Function to scroll and load all products
def scroll_down_page(driver, pause_time=2, max_attempts=8):
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

# Function to extract product name, link, and save to JSON doc
def extract_product_info(product_items, output_folder):
    count = 0
    for item in product_items:
        try:
            link_tag = item.find('a', href=True)
            product_link = link_tag['href'] if link_tag else None
            product_name_tag = item.find('p')
            product_name = product_name_tag.text.strip() if product_name_tag else None
            unique_key = str(uuid.uuid4())  # Generate unique key for each product
            count += 1

            if product_link and product_name:
                product_data = {
                    unique_key: {
                        'name': product_name,
                        'link': url + product_link
                    }
                }
                file_name = f"{unique_key}.json"
                file_path = os.path.join(output_folder, file_name)
                with open(file_path, 'w') as json_file:
                    json.dump(product_data, json_file, indent=4)
        except Exception as e:
            print(f"Error extracting or saving data: {e}")
    return count

# Function to extract features for each product
def extract_features(product_link):
    print(f"Visiting product page: {product_link}")
    driver.get(product_link)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    custom_pdp_div = soup.find('div', class_='custom-pdp')
    if not custom_pdp_div:
        print("Error: 'custom-pdp' div not found")
        return []

    pdp_features_link = custom_pdp_div.find('div', id='PDPFeaturesLink', class_='PDPFeaturesSlot')
    if not pdp_features_link:
        print("Error: 'PDPFeaturesLink' div not found")
        return []

    features = []

    # Check and click See more features button
    try:
        see_more_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "see_more_features_button"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
        time.sleep(2)
        see_more_button.click()
        print("Clicked on 'See more features' button")
        time.sleep(2)

    except (NoSuchElementException, TimeoutException):
        print("When button not found or timed out, proceeding.")
    except ElementClickInterceptedException:
        print("Element click intercepted, trying JavaScript click.")
        driver.execute_script("arguments[0].click();", see_more_button)
        time.sleep(2)
    except Exception as e:
        print(f"An error occurred while clicking the 'See more features' button: {e}")

    # Attempt 1: Extract features from 'custom-product-features__components' div
    product_features_sections = pdp_features_link.find_all('div', class_='custom-product-features__components')
    if product_features_sections:
        # print(f"Found {len(product_features_sections)} custom-product-features__components")
        for product_features_section in product_features_sections:
            feature_points = product_features_section.find_all('p')
            for feature in feature_points:
                feature_text = feature.text.strip()
                features.append(feature_text)
                # print(f"Feature found: {feature_text}")

    # Attempt 2:  extraction from alternate HTML structure
    if not features:
        # print("Checking for alternate feature structure)
        inline_content_div = soup.find('div', id='ccs-inline-content')
        if inline_content_div:
            # print("Found ccs-inline-content")
            feature_blocks = inline_content_div.find_all('div', class_='ccs-cc-inline-single-feature')
            for feature_block in feature_blocks:
                feature_title = feature_block.find('h3')
                feature_desc = feature_block.find('div', class_='ccs-cc-inline-feature-content')
                if feature_title and feature_desc:
                    feature_text = f"{feature_title.text.strip()}: {feature_desc.text.strip()}"
                    features.append(feature_text)
                    # print(f"Feature found: {feature_text}")

    return features

# Function to update product features in the existing JSON docs
def update_product_features(output_folder):
    for file_name in os.listdir(output_folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(output_folder, file_name)
            with open(file_path, 'r') as json_file:
                product_data = json.load(json_file)
            product_uuid = list(product_data.keys())[0]
            product_link = product_data[product_uuid].get('link')
            features = extract_features(product_link)
            product_data[product_uuid]['features'] = features
            # print(f"Features extracted for {product_data[product_uuid]['name']}: {features}")
            with open(file_path, 'w') as json_file:
                json.dump(product_data, json_file, indent=4)

# to scroll
scroll_down_page(driver, pause_time=3)

# For parsing
soup = BeautifulSoup(driver.page_source, 'html.parser')
product_items = soup.find_all('div', class_='custom-product-grid-item__content')

# Creating folder
output_folder = 'Corpus'
os.makedirs(output_folder, exist_ok=True)

# Extracting list of product and links
total_products = extract_product_info(product_items, output_folder)

# Updating features for each product
update_product_features(output_folder)

driver.quit()
