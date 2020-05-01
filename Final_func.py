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
Input: Basket of URLs
Output: Dataframe consisting of prices of the item on Amazon, Target, and Walmart websites
'''
def scraper(url_list, path):

    #loop through entries in list of URLs
    for amazon_url in url_list:
        #empty dictionary to store output
        row_results = {}

        
        #find product on Amazon
        amazon_driver = Chrome(executable_path=path)
        amazon_driver.get(amazon_url)
        #wait for the webpage to load
        time.sleep(5)

        #grab product name from Amazon
        try:
            amazon_name = amazon_driver.find_element_by_xpath('//*[@id="priceblock_ourprice"]').text
            row_results['amazon_price'] = amazon_name
        except:
            row_results['amazon_price'] = 'Price not found'
        
        #get Amazon price, if price is no longer available append 'Price not found'
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
        
        #otherwise get UPC from ASIN
        #note: can only look up 10 items per hour
        else:
            print("Item not found in ASIN-UPC dictionary. \nLooking up the UPC.")
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
            

        #find product on Target
        target_driver = Chrome(executable_path=path)
        target_url = 'https://www.target.com/s?searchTerm=' + upc_id
        target_driver.get(target_url)
        #wait for the webpage to load
        time.sleep(5)
        
        #get Target name if the item is found on Target 
        try:
            target_name = target_driver.find_element_by_xpath('//*[@id="mainContainer"]/div[3]/div[2]/div/div[1]/div[3]/div/ul/li/div/div[2]/div/div/div/div[1]/div[1]/a').text
            row_results['target_name'] = target_name
        except:
            row_results['target_name'] = "Item not found"
        
        #get Target price if item was found on Target
        try:
            target_price = target_driver.find_element_by_xpath('//*[@id="mainContainer"]/div[3]/div[2]/div/div[1]/div[3]/div/ul/li/div/div[2]/div/div/div/div[2]/span').text
            row_results['target_price'] = target_price
        except:
            row_results['target_price'] = "Price not found"
 
        target_driver.quit()
    

        #find product on Walmart
        walmart_driver = Chrome(executable_path=path)
        walmart_url = 'https://www.walmart.com/search/?query=' + upc_id
        walmart_driver.get(walmart_url)
        
        names_prices = walmart_driver.find_elements_by_xpath("//div[contains(@class, 'tile-content Grid-col u-size-8-10-l list-description-wrapper')]")
        
        #get Walmart name and price if product was found on Walmart
        if len(names_prices) == 0:
            row_results['walmart_name'] = 'Item not found'
            row_results['walmart_price'] = 'Price not found'
        else:
            for i in names_prices:
                if 'Pack' not in i.text:
                    #if name of the product from Walmart has already been looked up do not scrape again
                    price_list = i.text.split('\n')
                    row_results['walmart_name'] = price_list[price_list.index('Product Title')+1]
                    row_results['walmart_price'] = price_list[price_list.index('Current Price')+1]
                    
        walmart_driver.quit()

        
        #save results at time of scrape        
        timeofscrape = {}
        timeofscrape['scraped_at'] = str(datetime.today())
        timeofscrape['item'] = row_results
        with open('price_monitor.json', 'a') as pm:
            pm.write(json.dumps(','+timeofscrape))


'''
Pooling to optimize runtime of the function
'''
# We utilize a generator to split the input list into 4 lists so that we can run reach on one of our 4 CPUs
def chunkify(lst, n):
    """builds generator for dividing input lst into n chunks"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]



'''
Price tracking tool for a "Window Shopper"
Input: a search string, a number of items and a low and high value for that product.
    Note: input search term as a space seperated string only. 
Output: n items that match the price criteria for the item.
'''
def find_top_n(search_term: str, n: int, low_price: float, high_price: float, min_reviews: int, min_rating: float):
    final_items = []
    updated_search = search_term.replace(' ', '+')
    for page_number in count(1):
        if len(final_items) == n:
            driver.close()
            return final_items
        if page_number >= 9:
            print('The query has gone through 8 pages of items, but only {} have matched the criteria. The query has halted and your basket will contain this many itenms, as there are not likely to be more matches'.format(len(final_items)))
            break
            driver.close()
        page = True
        driver = webdriver.Chrome(executable_path=path)
        search = driver.get('https://www.amazon.com/s?k={0}&page={1}&qid=1586809805&ref=sr_pg_3'.format(updated_search, page_number))
        while page:
            for i in count(0):
                item = driver.find_elements_by_css_selector('div[data-index="{}"]'.format(i))
                if len(item) == 0:
                    # go to next page and start iterator over?
                    page = False
                    break
                try:
                    price = item[0].find_element_by_class_name('a-price').text
                    final_price = float(price.replace('$',"").replace('\n', '.'))
                except:
                    final_price = 0
                asin = item[0].get_attribute('data-asin')
                if asin != '':    
                    if final_price >= low_price:
                        if final_price <= high_price:
                            reviews = item[0].find_elements_by_css_selector('span[aria-label]')
                            try:
                                rating = float(reviews[0].get_attribute('aria-label')[:3])
                            except:
                                rating = 0
                            try:
                                num_reviews = int(reviews[1].get_attribute('aria-label').replace(',',''))
                            except:
                                num_reviews = 0 
                            if num_reviews >= min_reviews:
                                if rating >= min_rating:
                                    url = 'https://www.amazon.com/dp/' + asin
                                    if url not in final_items:
                                        final_items.append(url)
                if len(final_items) == n:
                    driver.close()
                    return final_items
    return(final_items)



'''
Main function
Input: Buyer type
Output: Corresponding function and its output
'''
buyer_type = input('Are you an Informed Buyer (I) or a Window Shopper (W)? ').strip().upper()
prices = pd.DataFrame(columns=['scrape_time', 'amazon_name', 'amazon_price', 'target_name','target_price', 'walmart_name', 'walmart_price'])
path = '/usr/local/bin/chromedriver'

#basket of items as URL
with open('baskets/basket_list.json') as l:
  basket_list = json.load(l)
#basket of items as ASIN-UPC
with open('baskets/allusers.json') as f:
  ASIN_dict = json.load(f) 

  
def price_scraper():
    buyer_type = input('Are you an Informed Buyer (I) or a Window Shopper (W)? ').strip().upper()
    '''Informed buyer'''
    if buyer_type == 'I':
        basket_type = input('Are you using a new list (N) or existing (E)? ').strip().upper()
        if basket_type == 'E':
            basket = basket_list
        elif basket_type == 'N':
            basket = []
            N = int(input('How many products would you like in your basket? '))
            for n in range(N):
                item = input('Paste Amazon links of the product you want to track and press Enter key when done ')
                if item == '':
                    print('Invalid input.')
                    return
                else:
                    basket.append(item)
        #run the scraper
        runtime = {}
        start = time.time()
        runtime['start_scrape'] = str(datetime.today())

        #for less than 4 items in basket, run regular scraper
        if len(basket)<4:
            scraper(basket,path)
        #else, run pool
        else:
            # Due to the particulars of pooling, we need to create a partial version of scraper that already has the path defined
            scraper_partial = partial(scraper, path=path)
            chunked_basket = list(chunkify(basket, 4))
            with Pool(4) as p:
                p.map(scraper_partial, chunked_basket)

        end = time.time()
        runs = end - start
        runtime['runtime'] = str(runs)
        with open('runtime.json', 'a') as rt:
            json.dump(runtime, rt)
    '''Window Shopper'''
    elif buyer_type == 'W':
        print('Please provide some information to narrow your search: ')
        search_term = input('Enter a type of product you want to purchase and press Enter key when done: ')

        if search_term == '':
            print('Invalid input.')
            return

        else:
            n = int(input('Select number of pages you would like to see and press Enter key when done: '))
            low_price = float(input('Select lowest price and press Enter key when done: '))
            high_price = float(input('Select highest price and press Enter key when done:'))
            min_reviews = int(input('Select minimum number of reviews and press Enter key when done: '))
            min_rating = float(input('Select minimum rating and press Enter key when done: '))
            basket = find_top_n(search_term, n, low_price, high_price, min_reviews, min_rating)
        #run the scraper
        #for less than 4 items in basket, run regular scraper
        if len(basket)<4:
            scraper(basket,path)
        #else, run pool
        else:
            # Due to the particulars of pooling, we need to create a partial version of scraper that already has the path defined
            scraper_partial = partial(scraper, path=path)
            chunked_basket = list(chunkify(basket, 4))
            with Pool(4) as p:
                p.map(scraper_partial, chunked_basket)



price_scraper()