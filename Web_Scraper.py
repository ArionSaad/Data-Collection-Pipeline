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
        #<span class="title">Steam Deck</span>  ignore steam deck
        #//*[@id="search_resultsRows"] all the items are this path's children 
        #first request the html of the page
        # this_URL = driver.current_url
        # this_page = requests.get(this_URL)
        # this_soup = BeautifulSoup(this_page.text, 'html.parser')
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
