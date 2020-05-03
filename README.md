# Python Price Project
Price tracking project for NYU DSGA-3001 Advanced Python course
### Authors: 
- Anu-Ujin Gerelt-Od
- Khasi-Marc Jamieson
- Nathan Griffin
- Paula Kiatkamolwong
- Tinatin Nikvashvili
- Will Egan
#### Code:
Both files contain the same code, but the ipynb has sample outputs
- group04_pricemonitorpy.py
- group04_pricemonitornb.ipynb
#### Files:
- Basket of items: basket_list.json
- ASIN-UPC dictionary: allusers.json 
- Output: price_monitor.json (Informed Buyer), price_scraper.json (Window Shopper)
- Runtime over 2 weeks: runtime.json

### Abstract:
In this project we tracked prices across three major e-commerce companies: Amazon, Target and Walmart. We enable users to track baskets of items over time by providing specific URLs of items from Amazon. We call these buyers informed buyers. If buyers prefer to only check the price of items at a given time instead of keeping track over time and not provide specific URLs, they can do that by providing a general description of items, such as an ’air fryer’ or ’keyboard’. We call these buyers windows shoppers. Once the informed buyer provides a basket of items to track, our model starts scraping and collecting information on prices of these items across the three retailers every day over time until the user stops wanting to collect information on a given basket. Users can explore price data and check how prices change over time or which retailer sells a given item for the cheapest price at a given time by exploring graph of the prices. We used different optimization techniques learned in class to make our scraper more efficient. To test our scraper, we scraped prices on 7 baskets of items (68 items total) for two weeks. The result and details of our approach and implementations are described in the write-up.

#### Environment requirements:
- Selenium: pip install selenium
- Chromedriver: pip install chromedriver_installer
