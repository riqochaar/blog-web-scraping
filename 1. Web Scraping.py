# WEB SCRAPING
# Import modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# Configure chrome driver
pathDriver = 'chromedriver.exe'
s = Service(pathDriver)
driver = webdriver.Chrome(service = s)
driver.implicitly_wait(5)

# List of channels
channels = ['TEDEd', 'veritasium', 'kurzgesagt', 'TierZoo', 'MinutePhysics', 'numberphile', 'CGPGrey']

# Initialise dataframe
df = pd.DataFrame()

# Extract video data from channel
for channel in channels:
    print(channel)
    # Load channel
    youtubeChannel = 'https://www.youtube.com/@' + channel + '/videos'
    driver.get(youtubeChannel)

    if channels.index(channel) == 0:
        # Select 'Accept All' button
        buttonAcceptAll = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/form[2]/div/div/button/span')
        driver.execute_script("arguments[0].click();", buttonAcceptAll)

    # Scroll down page to load all videos
    newHeight = 0
    oldHeight = 0
    while True:
        oldHeight = driver.execute_script("return document.documentElement.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        newHeight = driver.execute_script("return document.documentElement.scrollHeight")
        print(oldHeight, newHeight)
        if newHeight == oldHeight:
            break

    # Find videos data in page
    videos = driver.find_elements(By.CLASS_NAME, 'style-scope ytd-rich-grid-media')

    # Extract video title, number of views and date
    videoList = []
    for Video in videos:
        if len(videoList) % 100 == 0:
            print(len(videoList))
        title = Video.find_element(By.XPATH, './/*[@id="video-title"]').text
        views = Video.find_element(By.XPATH, './/*[@id="metadata-line"]/span[1]').text
        date = Video.find_element(By.XPATH, './/*[@id="metadata-line"]/span[2]').text
        VideoItem = {
            "Title" : title,
            "Views" : views,
            "Published Since" : date
        }
        videoList.append(VideoItem)

    # Save data as a dataframe
    dfChannel = pd.DataFrame(videoList)

    # Add additional data
    dfChannel['Channel'] = channel
    dfChannel['Subscribers'] = driver.find_element(By.XPATH, './/*[@id="subscriber-count"]').text

    df = pd.concat([df, dfChannel], ignore_index=True)

# Close the driver
driver.quit()

# Save raw data
df.to_excel('Raw.xlsx')
