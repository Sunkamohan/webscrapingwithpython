from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# imports here
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time



driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Define the number of pages to scrape
num_pages = 5  # Adjust as needed
# Create a list to store the data for each product
category_list = []
items = ["Apple",
         "OnePlus",
         "Samsung",
         # "Nillkin",
         # "Nokia",
         # "Motorola",
         # "realme",
         # "Lava",
         # "Redmi",
         # "Vivo",
         # "Oppo",
         # "SKYSHOP",
         # "Ghostek",
         # "imluckies"
         ]
for category in items:
    print(category, '-----------category')
    product_data_list = []
    # Loop through multiple pages
    for page_num in range(1, num_pages + 1):
        base_url = f"https://www.amazon.in/s?k={category.lower().strip()}&page={page_num}"
        # base_url = f"https://www.amazon.in/s?k={category.lower().strip()}&page={page_num}&qid=1691635055"
        # base_url = "https://www.amazon.in/s?i=electronics&bbn=1389401031&rh=n%3A1389401031%2Cp_89%3AApple&dc&page={a}&qid=1691586447&rnid=3837712031&ref=sr_pg_{b}"
        # base_url.format(k=category.lower(),a=page_num)
        print("Base url=======> ", base_url)
        # driver = webdriver.Chrome()
        driver.get(base_url)
        driver.maximize_window()
        time.sleep(3)
        print(page_num, 'page')
        # scroll down 2 times
        # increase the range to sroll more
        n_scrolls = 1
        for j in range(0, n_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        time.sleep(3)
        links = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                     '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')))

        anchors = [a.get_attribute('href') for a in links]
        print(anchors, len(anchors))

        # follow each image link and extract only image at index=1
        for a in anchors:
            product_details = {}
            driver.get(a)
            time.sleep(1)
            try:
                title = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//span[@id="productTitle"]'))).text
            except:
                title = "empty"
            time.sleep(1)

            try:
                img = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, 'landingImage'))).get_attribute('src')
            except:
                img = driver.find_element(by=By.CLASS_NAME,
                                          value="la-dynamic-image a-stretch-horizontal").get_attribute('src')

            time.sleep(1)
            try:
                price_element = driver.find_element(By.XPATH,
                                                    "//span[@class='a-price aok-align-center reinventPricePriceToPayMargin priceToPay']")

                # Extract the price text
                price = price_element.text
            except:
                pass

            time.sleep(1)
            try:
                savings_element = WebDriverWait(driver, 12).until(EC.presence_of_element_located((By.XPATH,
                                                                                                  "//span[@class='a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage']")))

                # Extract the savings percentage text
                savings_percentage = savings_element.text
            except:
                savings_percentage = None
            time.sleep(1)
            # Find the <table> element
            try:
                table_element = driver.find_element(By.XPATH, "(//table[@class='a-normal a-spacing-micro'])[1]")
            except:
                table_element = driver.execute_script('return document.querySelector(".a-normal.a-spacing-micro");')
            time.sleep(1)
            if table_element:
                # Find all <tr> elements within the table
                try:
                    rows = table_element.find_elements(By.TAG_NAME, "tr")
                except:
                    rows = table_element.find_elements(By.CLASS_NAME,"a-spacing-small")
                time.sleep(1)

                if rows:
                    # Loop through each row and extract the data
                    for row in rows:
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) > 1:
                                label = cells[0].text.strip()
                                value = cells[1].text.strip()
                                if label and value:  # Check if label and value are not empty
                                    print(label + ":", value)
                                    product_details[label] = value
                        except:
                            pass
                else:
                    pass
            else:
                pass

            time.sleep(1)
            # Extract ul/li elements
            try:
                ul_element = driver.find_element(By.XPATH, "//ul[@class='a-unordered-list a-vertical a-spacing-mini']")
                li_elements = ul_element.find_elements(By.XPATH, "./li")

                # Extract bullet point text and add to product_details as paragraphs
                paragraphs = []
                for li in li_elements:
                    item_text = li.find_element(By.XPATH, "./span[@class='a-list-item']").text.strip()
                    paragraphs.append(item_text)

                # Join the paragraphs into a single string and add to product_details
                description = '\n'.join(paragraphs)
                time.sleep(1)
            except:
                pass
            # Extract data-csa-c-asin value
            asin_value = driver.find_element(By.XPATH, "//div[@id='title_feature_div']").get_attribute(
                'data-csa-c-asin')

            time.sleep(1)
            data = {
                'title': title,
                'image': img,
                "price": price,
                "savings_percentage": savings_percentage,
                "link": a,
                "product_details": product_details,
                "description": description,
                "unique_code": asin_value,
            }
            print(data)
            # Append the data dictionary to the list
            product_data_list.append(data)

        time.sleep(1)
    category_save = {"category": category, "products": product_data_list}
    category_list.append(category_save)
    time.sleep(10)
driver.close()

# Save the JSON data to a file
with open('../product_data.json', 'w') as json_file:
    json.dump(category_list, json_file, indent=4)

# Print the JSON data to the console
print("Data exported to product_data.json")
