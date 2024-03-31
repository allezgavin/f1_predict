#!/usr/bin/env python
# coding: utf-8

# In[1]:


import datetime
MINIMUM_UPDATE_INTERVAL = datetime.timedelta(days=1)
src = 'sportsbook_data/fanduel.csv'


# In[2]:


import csv
import numpy as np
import pandas as pd


# In[6]:


from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep

options = {
    'proxy': {
        'http': 'http://3GJHIjCCFWGG8KLz:XAU1JUBDQtb59Tu2_country-us@geo.iproyal.com:12321',
        'https': 'https://3GJHIjCCFWGG8KLz:XAU1JUBDQtb59Tu2_country-us@geo.iproyal.com:12321',
    }
}

# We use sel_driver instead of the usual nomenclature driver to avoid conflict with racing driver
sel_driver = webdriver.Chrome(seleniumwire_options=options)


# In[7]:


url = 'https://sportsbook.fanduel.com/motorsport?tab=f1-race-props'

try:
    sel_driver.get(url)
    sel_driver.implicitly_wait(100) # Wait for dynamically loaded content
    sel_driver.find_element('xpath', '//div[@aria-label="Show more"]').click()
    tab = sel_driver.find_element('xpath',
                              '//ul[contains(., " Grand Prix") and contains(., "Podium Finish")][not(.//ul)]')
    podium_texts = tab.text.split('\n')
    
except NoSuchElementException as n:
    print('Cannot find the element. Error message as below:\n', n)

except Exception as e:
    print("An error occurred:\n", e)


# In[5]:


time = pd.Timestamp.now()
race = podium_texts[0]
podium_texts = podium_texts[2:-2]


# In[ ]:


def read_last_line(file_path):
    with open(file_path, mode='r') as file:
        # Using a CSV reader to read the file
        reader = csv.reader(file)
        # Convert reader to list and return the last row
        lines = list(reader)
        return lines[-1]


# In[ ]:


def calculate_elapsed_time(last_update_time):
    # Assuming last_update_time is a string in ISO 8601 format
    last_update_datetime = datetime.datetime.fromisoformat(last_update_time)
    current_datetime = datetime.datetime.now()
    elapsed_time = current_datetime - last_update_datetime
    return elapsed_time


# In[ ]:


def update_src(file_path):
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        for i in range(len(podium_texts)//2):
            driver = podium_texts[2*i]
            value = podium_texts[2*i+1]
            new_row = [race, 'podium finish', time, driver, value]
            writer.writerow(new_row)

    print("Fanduel podium finish data updated successfully.")
    # pd.read_csv(src).tail()


# In[ ]:


last_line = read_last_line(src)
last_update_time = last_line[2]
elapsed_time = calculate_elapsed_time(last_update_time)

if elapsed_time >= MINIMUM_UPDATE_INTERVAL:
    update_src(src)
else:
    print("No need to update the CSV file.")


# Run this in the command line to compile the .py file for task scheduling
# 
# jupyter nbconvert --to script proxy_scraper.ipynb

# In[ ]:




