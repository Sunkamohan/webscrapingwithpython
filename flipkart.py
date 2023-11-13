import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selectolax.parser import HTMLParser
from selenium.webdriver.support import expected_conditions as EC

def FlipkartItems():
    # Create Chrome options with headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode
    chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration, necessary for headless mode

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
    driver.maximize_window()
    href_list = []
    items = ['mobiles']
    for item in items:
        for i in range(1, 2):
            url = f'https://www.flipkart.com/search?q={item}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={i}'
            driver.get(url)
            time.sleep(1)
            n_scrolls = 2
            for j in range(0, n_scrolls):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                page_source = driver.page_source

                # Use selectolax to parse the HTML content
                html_data = HTMLParser(page_source)

                selector='div._13oc-S a'


                for node in html_data.css(selector):
                    href = node.attributes.get('href')
                    print(href)
                    if href:
                        href_list.append(href)

    print(href_list, len(href_list))

    products_images = []
    products = []

    # driver.quit()  # Close the WebDriver
    count = 0
    for j in href_list:

        link = f'https://www.flipkart.com{j}'

        # time.sleep(4)
        driver.get(link)
        # time.sleep(1)
        page_source = driver.page_source
        html_data = HTMLParser(page_source)

        # time.sleep(2)
        try:
            # Locate the ul element with class _3GnUWp
            ul_element = driver.find_element(By.CLASS_NAME, '_3GnUWp')

            # Find all li elements inside the ul
            li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

            products_images = []

            for li_element in li_elements:
                # Click on the li element
                li_element.click()

                # Wait for the image or iframe to load (you can adjust the wait time as needed)
                time.sleep(1)

                # Check if the image element exists
                image_element = None
                try:
                    image_element = driver.find_element(By.CSS_SELECTOR, '._2r_T1I._396QI4')
                except:
                    pass

                if image_element:
                    # Extract the src attribute of the image
                    image_src = image_element.get_attribute('src')
                    products_images.append(image_src)
                else:
                    # If image_element doesn't exist, find and extract the src attribute of the iframe
                    iframe_element = driver.find_element(By.CLASS_NAME, '_1JqCrR')
                    iframe_src = iframe_element.get_attribute('src')
                    products_images.append(iframe_src)
            # print("link--", link)
            # print(products_images, '-----images')
        except:
            products_images = []

        time.sleep(1)
        alert = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Product Details")]'))).click()

        # Initialize an empty dictionary to store the key-value pairs
        key_value_dict = {}

        # Locate the rows containing key-value pairs
        key_value_rows = html_data.css('.row')

        for row in key_value_rows:
            # Extract the key and value from each row
            key_element = row.css('.col-3-12._2H87wv')
            value_element = row.css('.col-9-12._2vZqPX')

            if key_element and value_element:
                key = key_element[0].text(deep=True, separator='', strip=False).strip()
                value = value_element[0].text(deep=True, separator='', strip=False).strip()
                # Replace spaces with underscores in the key
                key = key.lower().replace(' ', '_').replace('-', '_')

                # Make the key lowercase if it contains only lowercase letters
                if key.islower():
                    key = key.lower()
                # Store the key-value pair in the dictionary
                key_value_dict[key] = value

        product_selector = 'span.B_NuCI'  # Selector for product names
        price_selector = 'div._30jeq3._16Jk6d'  # Selector for product price
        offer_selector = 'div._3Ay6Sb._31Dcoz'  # Selector for product offer

        product_nodes = html_data.css(product_selector)
        price_nodes = html_data.css(price_selector)
        offer_nodes = html_data.css(offer_selector)

        if products_images:
            for product_node, price_node, offer_node in zip(product_nodes, price_nodes, offer_nodes):
                product_name = product_node.text(deep=True, separator='', strip=False).strip()
                price = price_node.text(deep=True, separator='', strip=False).strip()
                offer = offer_node.text(deep=True, separator='', strip=False).strip()
                product_dict = {"Url": link, 'product': product_name, 'price': price, 'offer': offer,
                                'images': products_images,
                                "product_details": key_value_dict}
                print(product_dict)
                products.append(product_dict)
                count += 1
                print(count)

        # print(products)
    # Remove duplicate dictionaries from the products list
    unique_products = []
    [unique_products.append(item) for item in products if item not in unique_products]

    return unique_products

unique_products = FlipkartItems()
# Save the JSON data to a file
with open(f'{time.strftime("%Y-%m-%d")}_flipkart_product_data{time.strftime("%H-%M-%S")}.json', 'w') as json_file:
    json.dump(unique_products, json_file, indent=4)
