from selenium import webdriver
from itertools import count
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime
from multiprocessing.pool import Pool
from functools import partial

'''
Price tracking tool for an "Informed buyer"
Input: URL
Output: dataframe consisting of prices of the item on Amazon, Target, and Walmart websites
'''

prices = pd.DataFrame(columns=['scrape_time', 'amazon_name', 'amazon_price', 'target_name','target_price', 'walmart_name', 'walmart_price'])
path = '/usr/local/bin/chromedriver'
#basket of items as URL
with open('baskets/basket_list.json') as l:
  basket_list = json.load(l)
#basket of items as ASIN-UPC
with open('baskets/allusers.json') as f:
  ASIN_dict = json.load(f)  


def scraper(url_list, path):
    global prices
  
    #loop through entries in list of URLs
    for amazon_url in url_list:
        # empty dictionary to store output
        row_results = {}
        # row_results['scrape_time'] = str(datetime.today())
        
        #find product on amazon
        amazon_driver = Chrome(executable_path=path)
        amazon_driver.get(amazon_url)
        #wait for the webpage to load
        time.sleep(10)

        #grab product name from amazon
        try:
            amazon_name = amazon_driver.find_element_by_xpath('//*[@id="productTitle"]').text
            row_results['amazon_name'] = amazon_name
        except:
            row_results['amazon_name'] = 'Item not found'
        
        #get amazon price, if price is no longer available append 'Price not found'
        try:
            row_results['amazon_price'] = amazon_driver.find_element_by_xpath('//*[@id="priceblock_ourprice"]').text
        except:
            row_results['amazon_price'] = 'Price not found'
        
        #get the ASIN
        if len(amazon_url.split('/')) == 5:
            asin = amazon_url.split('/')[4]
        else:
            asin = amazon_url.split('/')[5]
        amazon_driver.quit()
                
        #if UPC for a specific asin has already been looked up do not look up
        if asin in ASIN_dict:
            upc_id = ASIN_dict[asin]
        
        
        #getting UPC from ASIN
        else:
            upc_driver = Chrome(executable_path=path)
            upc_driver.get('https://www.synccentric.com/features/upc-asin/')
            box = upc_driver.find_element_by_id('scrollto')
            form = box.find_element_by_class_name('form-group')
            input = form.find_element_by_name('identifier')
            input.send_keys(asin)
            input.submit()
            #wait for the webpage to load
            time.sleep(10)
            id_list = upc_driver.find_element_by_class_name('col-sm-8').find_elements_by_tag_name('strong')
            upc_id = id_list[1].get_attribute('innerHTML')
            upc_driver.quit()
            
            #add the new asin --> upc to the dict
            ASIN_dict[asin] = upc_id
            
            #sleep so you are not locked out
            if len(basket_list) >10:
                time.sleep(10)




        #find product on target
        target_driver = Chrome(executable_path=path)
        target_url = 'https://www.target.com/s?searchTerm=' + upc_id
        target_driver.get(target_url)
        #wait for the webpage to load
        time.sleep(5)
        
        #get target name if the item is found on target 
        try:
            target_name = target_driver.find_element_by_xpath('//*[@id="mainContainer"]/div[3]/div[2]/div/div[1]/div[3]/div/ul/li/div/div[2]/div/div/div/div[1]/div[1]/a').text
            row_results['target_name'] = target_name
        except:
            row_results['target_name'] = "Item not found"
        
        #get target price if item was found on target
        try:
            target_price = target_driver.find_element_by_xpath('//*[@id="mainContainer"]/div[3]/div[2]/div/div[1]/div[3]/div/ul/li/div/div[2]/div/div/div/div[2]/span').text
            row_results['target_price'] = target_price
        except:
            row_results['target_price'] = "Price not found"
 
        target_driver.quit()
    


        #find product on walmart
        walmart_driver = Chrome(executable_path=path)
        walmart_url = 'https://www.walmart.com/search/?query=' + upc_id
        walmart_driver.get(walmart_url)
        time.sleep(5)
        names_prices = walmart_driver.find_elements_by_xpath("//div[contains(@class, 'tile-content Grid-col u-size-8-10-l list-description-wrapper')]")
        
        #get walmart name and price if product was found on walmart
        if len(names_prices) == 0:
            
            row_results['walmart_name'] = 'Item not found'
            row_results['walmart_price'] = 'Price not found'
        else:
            for i in names_prices:
                if 'Pack' not in i.text:
                    #if name of the product from walmart has already been looked up do not scrape again
                    
                    price_list = i.text.split('\n')
                    row_results['walmart_name'] = price_list[price_list.index('Product Title')+1]
                    row_results['walmart_price'] = price_list[price_list.index('Current Price')+1]
                    
        walmart_driver.quit()

        
        #save results at time of scrape        
        timeofscrape = {}
        timeofscrape['scraped_at'] = str(datetime.today())
        timeofscrape['item'] = row_results
        with open('price_monitor.json', 'a') as pm:
            pm.write(','+json.dumps(timeofscrape))
            
        prices = prices.append(row_results, ignore_index=True)



'''
Pooling to optimize runtime of the function
'''

'''
Due to the particulars of pooling, we need to create a partial version of scraper that already has the path
defined
'''
scraper_partial = partial(scraper, path=path)
'''
We utilize a generator to split the input list into 4 lists
so that we can run reach on one of our 4 CPUs
'''
def chunkify(lst, n):
    """builds generator for dividing input lst into n chunks"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
chunked_basket = list(chunkify(basket_list, 4))



#run the scraper
runtime = {}
start = time.time()
runtime['start_scrape'] = str(datetime.today())

i = 1
while i <2:
    with Pool(4) as p:
        p.map(scraper_partial, chunked_basket)
    i += 1

end = time.time()
runs = end - start
runtime['runtime'] = str(runs)
with open('runtime.json', 'a') as rt:
    json.dump(runtime, rt)