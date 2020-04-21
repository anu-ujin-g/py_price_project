# Window shopper / Uninformed buyer

def find_top_n(search_term: str, n: int, low_price: float, high_price: float, min_reviews: int, min_rating: float) -> list:
    '''
    This function takes as input a search string, a number of items and a low and high value for that product.
    Note: input search term as a space seperated string only. 
    It returns the n items that match the price criteria for the item. 
    '''
    final_items = []
    updated_search = search_term.replace(' ', '+')
    for page_number in count(1):
        if len(final_items) == n:
            return final_items
        if page_number >= 9:
            print('The query has gone through 8 pages of items, but only {} have matched the criteria. The query has halted and your basket will contain this many itenms, as there are not likely to be more matches'.format(len(final_items)))
            break
        page = True
        driver = webdriver.Chrome(executable_path='C:\Program Files\Chrome\chromedriver.exe')
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
                            rating = float(reviews[0].get_attribute('aria-label')[:3])
                            num_reviews = int(reviews[1].get_attribute('aria-label').replace(',',''))
                            if num_reviews >= min_reviews:
                                if rating >= min_rating:
                                    url = 'https://www.amazon.com/dp/' + asin
                                    if url not in final_items:
                                        final_items.append(url)
                if len(final_items) == n:
                    return final_items
    return(final_items)



# MAIN

buyer_type = input('Are you an Informed Buyer (I) or a Window Shopper (W)? ').strip().upper()

# This whole if can be converted to a function to add more URLs to the urls list

if buyer_type == 'I':
	basket = []
	item = input('Paste Amazon link of the product you want to track or press Enter key when done ')
	while True:
		if item == '':
			break
		else:		
			basket.append(item)
			item = input('Paste Amazon link of the product you want to track or press Enter key when done ')
	# print('Your basket: ', basket)	

# 	informed_buyer(basket)


else:    # window shopper
	pass