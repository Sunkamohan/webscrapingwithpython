import json
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

def count_repeated_letters(video_id):
    letter_count = {}
    repeated_letters = []

    for letter in video_id:
        if letter.isalpha():
            letter = letter.lower()
            letter_count[letter] = letter_count.get(letter, 0) + 1
            if letter_count[letter] > 1 and letter not in repeated_letters:
                repeated_letters.append(letter)

    return letter_count, repeated_letters

def scrape_videos(start_date, end_date):
    driver1 = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver2 = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver1.maximize_window()
    driver2.maximize_window()

    url = "https://www.youtube.com/@tseries/videos"
    driver1.get(url)
    time.sleep(1)
    print("proces collect links")
    try:
        last_height = driver1.execute_script("return document.documentElement.scrollHeight")
        while True:
            driver1.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            new_height = driver1.execute_script("return document.documentElement.scrollHeight")
            page_source = driver1.page_source
            html_data = HTMLParser(page_source)

            links = html_data.css('a.yt-simple-endpoint.focus-on-expand.style-scope.ytd-rich-grid-media')
            date_elements = html_data.css('span.inline-metadata-item.style-scope.ytd-video-meta-block')

            if date_elements:
                text_content = date_elements[-1].text(strip=True)
                if 'months ago' in text_content or 'month ago' in text_content:
                    anchors = [a.attributes.get('href') for a in links]

                    filtered_data = []
                    print("count of anchors",len(anchors))
                    for link in anchors:
                        print("driver 2 execute ")
                        driver1.get(f'https://www.youtube.com{link}')
                        time.sleep(1)
                        page_source = driver1.page_source
                        html_data = HTMLParser(page_source)
                        time.sleep(4)

                        try:
                            alert = WebDriverWait(driver1, 15).until(
                                    EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-button[@id='expand']"))).click()
                            time.sleep(5)

                            date_my_element = driver1.find_element(by=By.XPATH,
                                                                      value="/html[1]/body[1]/ytd-app[1]/div[1]/ytd-page-manager[1]/ytd-watch-flexy[1]/div[5]/div[1]/div[1]/div[2]/ytd-watch-metadata[1]/div[1]/div[4]/div[1]/div[1]/ytd-watch-info-text[1]/div[1]/yt-formatted-string[1]/span[3]")
                            date_my = date_my_element.text.replace('Premiered on', '').strip()
                            print(date_my, '-----date')
                        except Exception as e:
                            print("Date not available:", link, "remove")
                            continue  # Continue to the next iteration of the loop


                        date_str = date_my.replace('Premiered on', '').strip()
                        match = re.search(r'(\d{1,2}) (\w{3}) (\d{4})', date_str)

                        if match:
                            day = int(match.group(1))
                            month = match.group(2)
                            year = int(match.group(3))
                            # Convert the extracted date components to a datetime object
                            target_date = datetime(year, datetime.strptime(month, '%b').month, day)

                            if start_date <= target_date <= end_date:
                                video_id = link.split("v=")[1]
                                letter_count, repeated_letters = count_repeated_letters(video_id)
                                data_link = {
                                    "url": f'https://www.youtube.com{link}',
                                    "Date Uploaded": f'{day}-{month}-{year}',
                                    "Video ID": video_id,
                                    "Letter Count": letter_count,
                                    "Repeated Letters": repeated_letters
                                }
                                filtered_data.append(data_link)
                                print("Data for this link:", data_link)

                    with open("youtube_Tseries_data.json", "w") as outfile:
                        json.dump(filtered_data, outfile, indent=4)

                elif 'year ago' in text_content:
                    break

            if new_height == last_height:
                break
            last_height = new_height
    except Exception as e:
        print(e)

    driver1.quit()

# Define the start and end date for the video filtering
start_date = datetime(2023, 5, 22)
end_date = datetime(2023, 8, 8)

scrape_videos(start_date, end_date)
