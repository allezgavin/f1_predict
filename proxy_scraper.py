#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import csv
import numpy as np
import pandas as pd
import datetime


# In[ ]:


MINIMUM_UPDATE_INTERVAL = datetime.timedelta(days=1)
src = 'sportsbook_data/fanduel.csv'


# In[ ]:


from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep


# In[ ]:


import json
with open('config.json', 'r') as file:
    options = json.load(file)


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


def starts_with_any(string, substrings):
    for substring in substrings:
        if string.startswith(substring):
            return True
    return False


# In[ ]:


def update1_src(sel_driver, file_path, url = 'https://sportsbook.fanduel.com/motorsport?tab=formula-1'):
    sel_driver.get(url)
    sel_driver.implicitly_wait(100)

    show_more_buttons = sel_driver.find_elements('xpath', '//div[@aria-label="Show more"]')
    for button in show_more_buttons:
        button.click()

# Grand Prix-specific outright betting may not be available immediately. Hence we relax the condition a bit.
#     tab = sel_driver.find_element('xpath',
#                               '//ul[contains(., " Grand Prix") and contains(., "F1 Outrights")][not(.//ul)]')
    tab = sel_driver.find_element('xpath',
                              '//ul[contains(., "F1 Outrights")][not(.//ul)]')
    
    rates_text = tab.text.split('\n')
    #print(rates_text)
    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        time = pd.Timestamp.now()
        race = rates_text[0]
        i = 0
        
        if rates_text[1] == 'Outright Betting':
            i += 2
            while (i < len(rates_text)) and not rates_text[i+1].startswith('Show'):
                driver = rates_text[i]
                value = rates_text[i+1]
                try:
                    value = float(value)
                except Exception as e:
                    print("Invalid value:\n", value)
                    break
                new_row = [race, 'win', time, driver, value]
                writer.writerow(new_row)
                i += 2
                
            print("Fanduel outright betting data updated successfully.")
            i += 2
        
        if rates_text[i] == 'F1 Outrights':
            outright_items = ['F1 Drivers Championship','F1 Constructors Championship', 'Betting Without']
            item = ''
            i += 1
            while (i < len(rates_text)) and not rates_text[i].startswith('Overall H2H'):
                if rates_text[i+1].startswith('Show'):
                    i += 2
                    continue
                if starts_with_any(rates_text[i], outright_items):
                    item = rates_text[i]
                    i += 1
                    continue
                driver = rates_text[i]
                value = rates_text[i+1]
                try:
                    value = float(value)
                except Exception as e:
                    print("Invalid value:\n", value)
                    break
                new_row = [race, item, time, driver, value]
                writer.writerow(new_row)
                i += 2
                
            print("Fanduel season-long data updated successfully.")
                
        if rates_text[i].startswith('Overall H2H'):
            while (i+5 < len(rates_text)):
                item = rates_text[i]
                
                driver = rates_text[i+2]
                value = rates_text[i+3]
                try:
                    value = float(value)
                except Exception as e:
                    print("Invalid value:\n", value)
                    break
                new_row = [race, item, time, driver, value]
                writer.writerow(new_row)
                
                driver = rates_text[i+4]
                value = rates_text[i+5]
                try:
                    value = float(value)
                except Exception as e:
                    print("Invalid value:\n", value)
                    break
                new_row = [race, item, time, driver, value]
                writer.writerow(new_row)
                
                i += 7
    
            print('Fanduel H2H data updated successfully.')


# In[ ]:


# This may not be available immediately after the last Grand Prix finishes
def update2_src(sel_driver, file_path, url = 'https://sportsbook.fanduel.com/motorsport?tab=f1-race-props'):
    try:
        sel_driver.get(url)
        sel_driver.implicitly_wait(100) # Wait for dynamically loaded content
        sel_driver.find_element('xpath', '//div[@aria-label="Show more"]').click()
        tab = sel_driver.find_element('xpath',
                                  '//ul[contains(., " Grand Prix") and contains(., "Podium Finish")][not(.//ul)]')
        podium_texts = tab.text.split('\n')
        race = podium_texts[0]
        podium_texts = podium_texts[2:-2]

    except NoSuchElementException as n:
        print('Cannot find the element. Error message as below:\n', n)

    except Exception as e:
        print("An error occurred:\n", e)
        
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        time = pd.Timestamp.now()
        
        for i in range(len(podium_texts)//2):
            driver = podium_texts[2*i]
            value = podium_texts[2*i+1]
            try:
                value = float(value)
            except Exception as e:
                print("Invalid value:\n", value)
                break
            new_row = [race, 'podium finish', time, driver, value]
            writer.writerow(new_row)

    print("Fanduel podium finish data updated successfully.")
    # pd.read_csv(src).tail()


# In[ ]:


def update_src_all(file_path):
    # We use sel_driver instead of the usual nomenclature driver to avoid conflict with racing driver
    sel_driver = webdriver.Chrome(seleniumwire_options=options)
    
    # Must use the same driver, or the "options" dictionary would be mutated and reset.
    update1_src(sel_driver, file_path)
    update2_src(sel_driver, file_path)
    
    sel_driver.quit()


# In[ ]:


test_mode = True

if test_mode:
    src = 'sportsbook_data/fanduel_test.csv'
    update_src_all(src) # forced update

else:
    last_line = read_last_line(src)
    last_update_time = last_line[2]
    elapsed_time = calculate_elapsed_time(last_update_time)

    if elapsed_time >= MINIMUM_UPDATE_INTERVAL:
        update_src_all(src)

    else:
        print("No need to update the CSV files.")


# Run this in the command line to compile the .py file for task scheduling
# 
# jupyter nbconvert --to script proxy_scraper.ipynb

# In[ ]:




