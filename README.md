# Data-Collection-Pipeline

> An implementation of an industry grade data collection pipeline that runs scalably in the cloud. 

## Milestone 1

- The website that this project will collect data from is https://store.steampowered.com/ . This is a storefront with many unique sources of data from images, prices, tags, comments, reviews and various other details. The data collected from a platform like this would be valuable for anyone in the video games industry from developers, publishers, journalists to customers.  

## Milestone 2

- Installed the Selenium webdriver for chrome.
- Created a class that will scrape the storefront for the top selling games.
- Created method that will bypass cookie preference pop up.
- Created methods within the class that will navigate to the top seller page and make a list of the links to each game's store page.
- Used if __name__ == "__main__" to make sure the code only runs if the file is run directly rather than on any import

```python

from selenium import webdriver
import requests
from bs4 import BeautifulSoup 
from time import sleep

driver = webdriver.Chrome()

class Scraper:
    def __init__(self):
        self.URL = "https://store.steampowered.com/"

        driver.maximize_window()

        driver.get(self.URL)
        
        sleep(5)
        self.cookie_button() #get rid of cookies pop up

        # sleep(2)
        # self.scrolling()

        sleep(1)
        self.topseller() # go to the top sellers page

        sleep(1)
        self.make_list()
        pass

    def topseller(self):
        try:
            top_seller_link = driver.find_element_by_xpath('//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div[1]/div[8]/a[1]')
            top_seller_link.click()
        finally:
            pass

    def cookie_button(self):
        try:
            reject_cookie_button = driver.find_element_by_xpath('//*[@id="rejectAllButton"]')
            reject_cookie_button.click()
        except AttributeError:
            driver.switch_to('#cookiePrefPopup')
            reject_cookie_button = driver.find_element_by_xpath('//*[@id="rejectAllButton"]')
            reject_cookie_button.click()
        finally:
            pass
    
    def scrolling(self):
        driver.execute_script("window.scrollBy(0,2000)","")

    def make_list(self):
        self.game_list = []    
        game_container = driver.find_element_by_xpath('//*[@id="search_resultsRows"]') # this container holds all the top games
        top_list = game_container.find_elements_by_xpath('./a')
        top_list_links = [elem.get_attribute('href') for elem in top_list] # this extracts the hyperlinks to the individual store page 
        #print(top_list_links[1])
        for i in range(10):
            self.game_list.append(top_list_links[i])
            pass
        print(self.game_list)
        pass
        


    pass
    
if __name__ == "__main__":
    scrape = Scraper()
```python

## Milestone 3
