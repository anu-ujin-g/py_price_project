# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import selenium

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Amazon

driver = webdriver.Chrome(executable_path='C:\Program Files\Chrome\chromedriver.exe')

driver.get('https://www.amazon.com/1550-Watt-Programmable-Reheating-Dehydrating-AF101/dp/B07FDJMC9Q/ref=sr_1_1_sspa?crid=15FV65V3IHCD9&dchild=1&keywords=air+fryer&qid=1585838679&sprefix=air+f%2Caps%2C181&sr=8-1-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEzSFFKSjlXSllKN1M3JmVuY3J5cHRlZElkPUEwMzEzNDgzTTZZVlpTWlpPS0laJmVuY3J5cHRlZEFkSWQ9QTAzODA0OTEzVDc5QktPOElHNFVaJndpZGdldE5hbWU9c3BfYXRmJmFjdGlvbj1jbGlja1JlZGlyZWN0JmRvTm90TG9nQ2xpY2s9dHJ1ZQ==')

x = driver.find_element_by_id('productDetails_detailBullets_sections1')

my_list = x.find_elements_by_tag_name('tr')

my_test = my_list[4]

output = my_test.find_element_by_tag_name('td').get_attribute('innerHTML')

final = output.strip()
    
url = 'www.amazon.com/dp/' + final

price = float(driver.find_element_by_id('priceblock_ourprice').get_attribute('innerHTML')[1:])

title = driver.find_element_by_id('productTitle').get_attribute('innerHTML').strip()

# Getting UPC from ASIN
upc_driver = webdriver.Chrome(executable_path='C:\Program Files\Chrome\chromedriver.exe')

upc_driver.get('https://www.synccentric.com/features/upc-asin/')

box = upc_driver.find_element_by_id('scrollto')

form = box.find_element_by_class_name('form-group')

input = form.find_element_by_name('identifier')

input.send_keys(final)

input.submit()

id_list = upc_driver.find_element_by_class_name('col-sm-8').find_elements_by_tag_name('strong')

upc_id = id_list[1].get_attribute('innerHTML')

# Target UPC 

target_driver = webdriver.Chrome(executable_path='C:\Program Files\Chrome\chromedriver.exe')

target_url = 'https://www.target.com/s?searchTerm=' + upc_id

target_driver.get(target_url)




    




