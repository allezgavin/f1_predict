#!/usr/bin/env python
# coding: utf-8

# Adapted from https://github.com/ritomsonowal/F1-Data-Analysis/blob/master/update.py

# In[1]:


import wget
import os, shutil
import zipfile


# In[2]:


print('===================================')
print('Updating CSV files')
print('===================================')


# In[3]:


folder = 'data/'


# In[4]:


# Remove outdated files
for file in os.listdir(folder):
    file_path = os.path.join(folder, file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)


# In[5]:


# Download csv zip
url = 'http://ergast.com/downloads/f1db_csv.zip'

wget.download(url, folder)

# Unzip csv files
zip_path = folder+'f1db_csv.zip'

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(folder)

# Delete zip file
os.remove(folder+'f1db_csv.zip')


# In[ ]:




