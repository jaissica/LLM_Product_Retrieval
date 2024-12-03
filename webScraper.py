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

# url = "https://electronics.sony.com/audio/headphones/c/all-headphones"
url = "https://electronics.sony.com/audio/soundbars/c/all-soundbars"
# url = "https://electronics.sony.com/audio/speakers/c/all-speakers"

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
    products = {}
    count = 0
    for item in product_items:
        try:
            link_tag = item.find('a', href=True)
            product_link = link_tag['href'] if link_tag else None
            product_name_tag = item.find('p')
            product_name = product_name_tag.text.strip() if product_name_tag else None
            unique_key = str(uuid.uuid4())  # Generate unique key for each product
            count += 1  # Increment count for each product

            if product_link and product_name:
                product_data = {
                    'name': product_name,
                    'link': url + product_link
                }
                products[unique_key] = product_data

                # Save each product to a separate JSON file
                file_name = f"{unique_key}.json"
                file_path = os.path.join(output_folder, file_name)
                with open(file_path, 'w') as json_file:
                    json.dump({unique_key: product_data}, json_file, indent=4)
        except Exception as e:
            print(f"Error extracting or saving data: {e}")
    return count, products

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
        # print("Specification container not found in modal after expansion.")
        return ["Specification container not found"]

    # Step 5: Parse the specifications in the container
    specification_container = soup.find('div', class_='full-specifications__specifications-list')
    specification_info = {}

    specification_cards = specification_container.find_all('div',
                                                           class_="full-specifications__specifications-single-card")
    if not specification_cards:
        # print("No specification cards found within specification container.")
        return ["No specification cards found"]

    for card in specification_cards:
        heading_tag = card.find('h3', class_="full-specifications__specifications-single-card__heading")
        if heading_tag:
            heading = heading_tag.text.strip()
            specification_info[heading] = []

        sub_list_items = card.find_all('div', class_="full-specifications__specifications-single-card__sub-list")
        for sub_item in sub_list_items:
            sub_heading_tag = sub_item.find('h4',
                                            class_="full-specifications__specifications-single-card__sub-list__name")
            sub_value_tag = sub_item.find('p',
                                          class_="full-specifications__specifications-single-card__sub-list__value")

            if sub_heading_tag and sub_value_tag:
                sub_heading = sub_heading_tag.text.strip()
                sub_value = sub_value_tag.text.strip()
                specification_info[heading].append({sub_heading: sub_value})
                # print(f"Added {sub_heading}: {sub_value} under {heading}")
            else:
                print("Sub-heading or value not found for a specification item.")

    # Final check to confirm if data was extracted
    if specification_info:
        # print(f"Specifications: {specification_info}")
        return specification_info
    else:
        # print("No specifications found after expansion.")
        return ["No specifications found after expansion"]

# Function to save product details
def get_product_details(product_url, product_name, product_id, output_folder):
    driver.get(product_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    product_details = {
        product_id: {
            'name': product_name,
            'link': product_url,
            'price': fetch_price(soup),
            'emi': fetch_emi(soup),
            'about_us': fetch_about_us(soup),
            'specification': fetch_specification(soup),
            'features': extract_features(product_url)  # Fetch features once and save
        }
    }

    output_file = os.path.join(output_folder, f"{product_id}.json")
    with open(output_file, 'w') as json_file:
        json.dump(product_details, json_file, indent=4)

# Function to extract features for each product
def extract_features(url):
    print(f"Visiting product page: {url}")
    driver.get(url)
    time.sleep(5)

    # to locate and click the "See More Features" button
    try:
        # print("Navigating to 'PDPFeaturesLink' section.")
        pdp_features_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#PDPFeaturesLink.PDPFeaturesSlot"))
        )
        # print("PDPFeaturesLink section found. Looking for 'See More Features' button.")

        see_more_button_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#PDPFeaturesLink .custom-product-features .see_more_features_button.container"))
        )
        see_more_button = see_more_button_container.find_element(By.CSS_SELECTOR, "button.sony-btn.sony-btn--primary-border")

        # print("See More Features button found. Clicking it to load additional features.")
        driver.execute_script("arguments[0].click();", see_more_button)
        time.sleep(2)
    except Exception as e:
        print(f"No 'See More Features' button found or click intercepted: {e}. Proceeding without clicking.")

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    features_dict = {}
    feature_set = set()
    orphan_headings = []

    # Attempt 1: Extract features from 'custom-product-features__components'
    # print("Extracting features from 'custom-product-features__components'.")
    additional_components = soup.find_all('div', class_='custom-product-features__components')

    for component in additional_components:
        heading = component.find('h2')
        paragraphs = component.find_all('p')

        heading_text = heading.text.strip() if heading else "All features"

        if heading_text not in features_dict:
            features_dict[heading_text] = []

        for paragraph in paragraphs:
            paragraph_text = paragraph.text.strip()
            if paragraph_text and paragraph_text not in feature_set:
                features_dict[heading_text].append(paragraph_text)
                feature_set.add(paragraph_text)
                # print(f"Feature paragraph found: {paragraph_text}")

    # Attempt2: Extract features from new structure: 'features-common__heading' and 'features-common__text'
    # print("Extracting features from the new structure: 'features-common__heading' and 'features-common__text'.")
    feature_sections = soup.find_all('div', class_='features-common')
    for section in feature_sections:
        heading = section.find('div', class_='features-common__heading')
        description_div = section.find('div', class_='features-common__other-content')

        heading_text = heading.text.strip() if heading else "All features"

        if heading_text not in features_dict:
            features_dict[heading_text] = []

        if description_div:
            paragraphs = description_div.find_all('p') if description_div else []
            for paragraph in paragraphs:
                description_text = paragraph.text.strip()
                if description_text and description_text not in feature_set:
                    features_dict[heading_text].append(description_text)
                    feature_set.add(description_text)
                    # print(f"New structure description found: {description_text}")
        else:
            # Handle case where text is directly inside 'features-common__text' without <p> tag
            description_text_div = section.find('div', class_='features-common__text')
            if description_text_div:
                description_text = description_text_div.text.strip()
                if description_text and description_text not in feature_set:
                    features_dict[heading_text].append(description_text)
                    feature_set.add(description_text)
                    print(f"New structure description found without <p> tag: {description_text}")

    #Attempt3:  Extract features from 'feature-images__conatiner' structure
    # print("Extracting features from 'feature-images__conatiner' structure.")
    feature_image_containers = soup.find_all('div', class_='feature-images__conatiner')
    for container in feature_image_containers:
        rows = container.find_all('div', class_='row feature-images__conatiner__info')

        for row in rows:
            cols = row.find_all('div', class_='col-sm-6 col-xxs-12')

            for col in cols:
                feature_common = col.find('div', class_='features-common')
                if feature_common:
                    heading = feature_common.find('div', class_='features-common__heading')
                    description_container = feature_common.find('div', class_='features-common__text')

                    heading_text = heading.text.strip() if heading else "All features"

                    if heading_text not in features_dict:
                        features_dict[heading_text] = []
                    description_text = ""
                    if description_container:
                        paragraphs = description_container.find_all('p')
                        if paragraphs:
                            description_text = ' '.join(p.text.strip() for p in paragraphs if p.text.strip())
                        else:
                            description_text = description_container.text.strip()

                    if description_text:
                        features_dict[heading_text].append(description_text)
                        feature_set.add(description_text)
                        print(f"Feature image container feature found: {heading_text}: {description_text}")
                    else:
                        orphan_headings.append(heading_text)

    #Attempt4:  Extract features from 'features-common__eyebrow', 'features-common__heading', and 'features-common__text'
    # print("Extracting features from 'features-common__eyebrow', 'features-common__heading', and 'features-common__text'.")
    eyebrow_sections = soup.find_all('div', class_='features-common')
    for section in eyebrow_sections:
        eyebrow = section.find('div', class_='features-common__eyebrow')
        heading = section.find('div', class_='features-common__heading')
        description_container = section.find('div', class_='features-common__text')

        eyebrow_text = eyebrow.text.strip() if eyebrow else ""
        heading_text = heading.text.strip() if heading else "All features"

        combined_heading = f"{eyebrow_text} {heading_text}".strip()

        if combined_heading not in features_dict:
            features_dict[combined_heading] = []

        if description_container:
            paragraphs = description_container.find_all('p') if description_container else []
            description_text = ""
            if paragraphs:
                description_text = ' '.join(p.text.strip() for p in paragraphs if p.text.strip())
            else:
                description_text = description_container.text.strip()

            if description_text and description_text not in feature_set:
                features_dict[combined_heading].append(description_text)
                feature_set.add(description_text)
                print(f"Eyebrow structure description found: {combined_heading}: {description_text}")
        else:
            orphan_headings.append(combined_heading)

    #Attempt5:  Extract features from 'ccs-cc-inline-feature-description' (new format found in provided HTML)
    # print("Extracting features from 'ccs-cc-inline-feature-description'.")
    inline_feature_descriptions = soup.find_all('div', class_='ccs-cc-inline-feature-description')
    for feature in inline_feature_descriptions:
        heading = feature.find('h3')  # Changed to 'h3' for this specific structure
        description_text = feature.get_text(strip=True)

        heading_text = heading.text.strip() if heading else "All features"

        if heading_text not in features_dict:
            features_dict[heading_text] = []

        if description_text and description_text not in feature_set:
            features_dict[heading_text].append(description_text)
            feature_set.add(description_text)
            # print(f"Inline feature description found: {heading_text}: {description_text}")

    # Combine features
    features = {}
    for heading, items in features_dict.items():
        if items:
            features[heading] = items
        else:
            orphan_headings.append(heading)

    # headings without descriptions
    for orphan_heading in orphan_headings:
        if orphan_heading not in features_dict:
            features[orphan_heading] = []

    return features

# Function to update product features in the existing JSON docs
def update_product_features(output_folder):
    for file_name in os.listdir(output_folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(output_folder, file_name)

            with open(file_path, 'r') as json_file:
                product_data = json.load(json_file)

            # Extract unique key and validate each product's fields
            product_uuid = list(product_data.keys())[0]
            product_info = product_data[product_uuid]

            # Ensure each required field exists; update with default values if missing
            product_info.setdefault('features', [])
            product_info.setdefault('price', "Price not found")
            product_info.setdefault('emi', "EMI info not found")
            product_info.setdefault('about_us', ["About Us info not found"])
            product_info.setdefault('specification', [])

            # Re-save the JSON file with updated or confirmed data
            with open(file_path, 'w') as json_file:
                json.dump(product_data, json_file, indent=4)

            print(f"Updated and validated JSON for product: {product_info['name']}")

# to scroll
scroll_down_page(driver, pause_time=2)
soup = BeautifulSoup(driver.page_source, 'html.parser')
product_items = soup.find_all('div', class_='custom-product-grid-item__content')


# Creating folder
# output_folder = 'Corpus/Headphones'
# output_folder = 'Corpus/Speakers'
output_folder = 'Corpus/Soundbars'

os.makedirs(output_folder, exist_ok=True)
# Extracting list of product and links

count, products = extract_product_info(product_items, output_folder)
print(f"Total products extracted: {count}")


for product_id, product in products.items():
    get_product_details(product['link'], product['name'], product_id, output_folder)
# Updating features for each product
update_product_features(output_folder)
driver.quit()
