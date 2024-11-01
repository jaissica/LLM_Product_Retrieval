import time
import json
import os
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementClickInterceptedException

driver = webdriver.Chrome()
product_page_url = "https://electronics.sony.com/audio/headphones/c/all-headphones"
# product_page_url = "https://electronics.sony.com/audio/soundbars/c/all-soundbars"
# product_page_url = "https://electronics.sony.com/audio/speakers/c/all-speakers"

driver.get(product_page_url)
time.sleep(3)

# Function to load all products by continuously scrolling until the end
def scroll_to_load_all_products():
    scroll_pause_time = 2
    max_attempts = 10  # Maximum scroll attempts without finding new products
    attempts = 0
    last_height = driver.execute_script("return document.body.scrollHeight")

    while attempts < max_attempts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")

        # Check if new products loaded
        if new_height == last_height:
            attempts += 1
        else:
            attempts = 0  # Reset attempts if new content loaded

        last_height = new_height

scroll_to_load_all_products()

soup = BeautifulSoup(driver.page_source, 'html.parser')
product_list = soup.find_all('div', class_='custom-product-grid-item__content')

# Function to extract product name, link, and add to a dictionary
def get_product_data(product_list):
    product_info = {}
    for item in product_list:
        try:
            link_element = item.find('a', href=True)
            product_url = link_element['href'] if link_element else None
            product_name = item.find('p').text.strip() if item.find('p') else None
            product_id = str(uuid.uuid4())

            if product_url and product_name:
                product_info[product_id] = {
                    'name': product_name,
                    'link': product_page_url + product_url
                }
        except Exception as e:
            print(f"Error getting product data: {e}")
    return product_info

# Extract price
def fetch_price(soup):
    price_element = soup.find('p', class_='product-pricing__amount')
    return price_element.text.strip() if price_element else "Price not found"

# Extract EMI
def fetch_emi(soup):
    emi_element = soup.find('div', class_='product__affirm__container')
    return emi_element.text.strip() if emi_element else "EMI info not found"

# Function to fetch About Us with the initial logic
def fetch_about_us(soup):
    about_us_info = []

    # Step 1: Close any visible modals that may block interaction
    def close_modal(xpath):
        try:
            modal_close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].click();", modal_close_button)
            print(f"Closed modal using {xpath}.")
            time.sleep(1)
        except Exception:
            print(f"No modal found for {xpath}, proceeding.")
    
    # Close all suspected modals
    close_modal('//*[@id="contentfulModalClose"]')
    close_modal('//*[@class="icon-close-black"]')

    # Step 2: Check if "See More" button exists, then attempt click
    see_more_exists = soup.find('div', class_='pdp-summary-highlights__seeMore')
    
    if see_more_exists:
        try:
            see_more_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pdp-summary-highlights__seeMore"))
            )
            see_more_button = see_more_container.find_element(By.CLASS_NAME, "sony-btn--primary-border")
            
            # Scroll to the button and try both direct and JavaScript click
            driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
            time.sleep(1)
            try:
                see_more_button.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", see_more_button)
            time.sleep(2)  # Allow time for content to load
        except Exception as e:
            print(f"Could not click 'See More': {e}")

    # Step 3: Capture the "About Us" content
    retries = 0
    while retries < 5:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        about_us_element = soup.find('div', class_='pdp-summary-highlights__content')

        if about_us_element:
            items = about_us_element.find_all('li')
            if items:
                about_us_info = [item.text.strip() for item in items]
                break

        retries += 1
        print("Retrying to load more 'About Us' items...")
        time.sleep(2)

    # Return results
    if about_us_info:
        return about_us_info
    else:
        return ["About Us info not found"]

# Dummy function for Specifications if needed
def fetch_specification(soup):
    # Step 1: Click the `+` icon to expand the specifications modal
    try:
        plus_icon = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "black_plus"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", plus_icon)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", plus_icon)  # JavaScript click to ensure activation
        # print("Clicked on '+' icon to expand specifications modal.")
        time.sleep(3)  # Wait for modal to open
    except Exception as e:
        # print(f"Error clicking '+' icon: {e}")
        return ["Failed to expand specifications"]

    # Step 2: Refresh `soup` to capture updated modal content
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Step 3: Check and click "See More" if visible within modal
    try:
        see_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".sony-btn.sony-btn--primary--inverse"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", see_more_button)  # JavaScript click on 'See More'
        # print("Clicked on 'See More' button for full specifications.")
        time.sleep(3)
    except Exception:
        print("No 'See More' button or already fully expanded.")

    # Step 4: Verify the modal specifications container has loaded
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "full-specifications__specifications-list"))
        )
        # print("Specification container detected.")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except TimeoutException:
        #print("Specification container not found in modal after expansion.")
        return ["Specification container not found"]

    # Step 5: Parse the specifications in the container
    specification_container = soup.find('div', class_='full-specifications__specifications-list')
    specification_info = {}

    specification_cards = specification_container.find_all('div', class_="full-specifications__specifications-single-card")
    if not specification_cards:
        #print("No specification cards found within specification container.")
        return ["No specification cards found"]

    for card in specification_cards:
        heading_tag = card.find('h3', class_="full-specifications__specifications-single-card__heading")
        if heading_tag:
            heading = heading_tag.text.strip()
            specification_info[heading] = []

        sub_list_items = card.find_all('div', class_="full-specifications__specifications-single-card__sub-list")
        for sub_item in sub_list_items:
            sub_heading_tag = sub_item.find('h4', class_="full-specifications__specifications-single-card__sub-list__name")
            sub_value_tag = sub_item.find('p', class_="full-specifications__specifications-single-card__sub-list__value")
            
            if sub_heading_tag and sub_value_tag:
                sub_heading = sub_heading_tag.text.strip()
                sub_value = sub_value_tag.text.strip()
                specification_info[heading].append({sub_heading: sub_value})
                #print(f"Added {sub_heading}: {sub_value} under {heading}")
            else:
                print("Sub-heading or value not found for a specification item.")

    # Final check to confirm if data was extracted
    if specification_info:
        # print(f"Specifications: {specification_info}")
        return specification_info
    else:
        #print("No specifications found after expansion.")
        return ["No specifications found after expansion"]

# Function to save product details
def get_product_details(product_url, product_name, product_id, output_folder):
    driver.get(product_url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    product_details = {
        'name': product_name,
        'link': product_url,
        'price': fetch_price(soup),
        'emi': fetch_emi(soup),
        'about_us': fetch_about_us(soup),
        'specification': fetch_specification(soup)
    }

    output_file = os.path.join(output_folder, f"{product_id}.json")
    with open(output_file, 'w') as json_file:
        json.dump(product_details, json_file, indent=4)

# Parse products and save data
products = get_product_data(product_list)
output_folder = 'Dataset/Headphones'
# output_folder = 'Dataset/Speakers'
# output_folder = 'Dataset/Soundbars'
os.makedirs(output_folder, exist_ok=True)

for product_id, product in products.items():
    get_product_details(product['link'], product['name'], product_id, output_folder)

driver.quit()