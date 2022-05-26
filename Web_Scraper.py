
import string
import requests
import uuid
import os
import json
import urllib.request
from bs4 import BeautifulSoup 
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from uuid import UUID 
from lxml import etree 

class Scraper:
    '''
        This class is for a Web scraper that will automatically collect data on the top selling games on Steam.

        It is populated with methods used to navigate the webpage, collect specific bits of information and then stores the information on a local json file. 
    '''
    def __init__(self, number_of_games: int, url: string,):

        self.driver = webdriver.Chrome() #Using Chrome as the browser for the selenium web driver  

        self.number_of_games = number_of_games # number of games that will have their data collected

        self.URL = url # URL to the home page of the website

        self._make_folder()
        
        self._open_browser()
        
        sleep(5)
        self._cookie_button() #get rid of cookies pop up

        sleep(1)
        self._go_to_top_seller() # go to the top sellers page

        sleep(1)

        self._filter_page()

        self.game_list = self._make_list_of_links(self.number_of_games) # List of links to the store page of the games

        self.game_dict = self._make_dictionary(self.number_of_games) # Dictionary where the data for each game will be stored

        self._collect_data(self.number_of_games)

        self._close_browser()

        pass

    def _make_folder(self):
        # This method creates a folder for the raw data to be saved locally.
        self.root_dir = os.path.dirname(os.path.abspath(__file__)) 
        self.raw_data_folder = 'raw_data'

        path = os.path.join(self.root_dir, self.raw_data_folder)
        try:
            os.mkdir(path)
        except:
            pass

    def _open_browser(self):
        # This method will open the browser using Selenium and maximise it. It will then go the home page of the store front
        self.driver.maximize_window()

        self.driver.get(self.URL)
    
    def _close_browser(self):
        #This method will close the browser

        self.driver.close()

    def _go_to_top_seller(self):
        # This method navigates to the top sellers page from the homepage of Steam.
        try:
            top_seller_link = self.driver.find_element(By.XPATH, '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div[1]/div[8]/a[1]')
            top_seller_link.click()
        finally:
            pass

    def _cookie_button(self):
        # This method is used to get rid of the cookie confirmation pop up.
        try:
            reject_cookie_button = self.driver.find_element(By.XPATH, '//*[@id="rejectAllButton"]')
            reject_cookie_button.click()
        except AttributeError:
            self.driver.switch_to('#cookiePrefPopup')
            reject_cookie_button = self.driver.find_element(By.XPATH, '//*[@id="rejectAllButton"]')
            reject_cookie_button.click()
        finally:
            pass
    
    def _scrolling(self):
        # This method is used to scroll down the web page.
        self.driver.execute_script("window.scrollBy(0,2000)","")

    def _filter_page(self):
        # This method filters the top selling page so only the games are showing
        button_filter_type = self.driver.find_element(By.XPATH, '//*[@id="additional_search_options"]/div[3]/div[1]')
        button_filter_type.click()

        sleep(2)
        
        button_filter_games = button_filter_type.find_element(By.XPATH, '//*[@id="narrow_category1"]/div[1]/span/span/span[2]') 
        button_filter_games.click()

        sleep(2)


    def _make_list_of_links(self, number: int) -> list: 
        # Makes a list of links of the top selling games which will then be parsed by other methods to extract data

        game_container = self.driver.find_element(By.XPATH, '//*[@id="search_resultsRows"]') # this container holds all the top games
        sleep(1)
        top_list = game_container.find_elements(By.XPATH, './a')
        sleep(1)
        
        top_list_links = [elem.get_attribute('href') for elem in top_list] # this extracts the hyperlinks to the individual store page 

        a_list = []

        for i in range(number):  # select the top 20 games on the list          
            a_list.append(top_list_links[i])
        
        return a_list

    def _make_dictionary(self, number: int) -> dict:
        # This method will create the dictionary to store all the data 

        a_dict = {}

        for i in range(number):
            a_dict[f'{i}'] = {}

        return a_dict            

    def make_soup(self, web_page: string): 
        # creates the soup from a url from which data can be extracted 

        page = requests.get(web_page)
        soup = BeautifulSoup(page.text, 'html.parser')

        return soup
    
    def get_product_ID(self, soup): 
        
        # generate a user friendly id unique to each game

        fish = soup.find(name ='div', attrs={'class':"glance_tags popular_tags"})

        prod_id = fish['data-appid']

        return prod_id      

    def generate_UUID(self): 
        
        # generate an UUID for each game
        unique_id = uuid.uuid4()
        uuid_str = str(unique_id)

        return uuid_str        

    def get_cover_image(self, soup): 
        
        #gets the cover image of the game

        fish = soup.find(name='img', attrs={'class':'game_header_image_full'})
        img = fish['src']

        return img      
    
    def get_game_title(self, soup): 
        
        # gets the game's title

        fish = soup.find(name='div', attrs={'id':'appHubAppName', 'class':'apphub_AppName'})
        name = fish.text

        return name
                     
    def get_game_tags(self):
        ## BROKEN 

        # Gets the tags for the game 

        for i in range(len(self.game_list)):
            # page = requests.get(self.game_list[i])
            # soup = BeautifulSoup(page.text, 'html.parser')
            soup = self.make_soup(i)
            fish =soup.find(name='div' , attrs={'class':"glance_tags popular_tags" })
            tag_list_html = fish.find_all('a')
            tag_list = [elem.text for elem in tag_list_html]

            self.game_dict[f'{i}']['Tags'] = tag_list

    def game_dev(self, soup):
        #Get the name of the developer

        fish = soup.find(name='div' , attrs={'class':"summary column", 'id':'developers_list' })
        fish_list = fish.find_all('a')
        dev_list = [elem.text for elem in fish_list]

        return dev_list            

    def game_pub(self, soup):
        #Get's the name of the publisher
        fish = etree.HTML(str(soup))
        try:
            pub = fish.xpath('//*[@id="game_highlights"]/div[1]/div/div[3]/div[4]/div[2]/a')[0].text            
        except: 
            pub = 'None'

        return pub     

    def release_date(self, soup):
        
        #Finds the release date

        fish = soup.find(name='div', attrs={'class':'date'})
        date = fish.text

        return date

    def make_game_folder(self, game_folder, a_dict):
        #this method makes a folder for each game and creates a json file of the data extracted 
        try:
            path = os.path.join(self.root_dir, self.raw_data_folder, game_folder)

            os.mkdir(path)

            with open(f'{path}/data.json', 'w') as fp:
                json.dump(a_dict, fp)
        
        except:
            pass
        
     

    def save_image_file(self, game_folder, img):
        #downloads the images

        try:
            path = os.path.join(self.root_dir, self.raw_data_folder, game_folder, 'images')
            os.mkdir(path)
            urllib.request.urlretrieve(img, f'{path}/1.jpg')
        except:
            pass


    def _collect_data(self, number):
        # This method runs all the methods for collecting data

        for i in range(number):
            store_page = self.game_list[i]
            soup = self.make_soup(store_page)

            prod_id = self.get_product_ID(soup)
            self.game_dict[f'{i}']['ID'] = prod_id 

            img = self.get_cover_image(soup)
            self.game_dict[f'{i}']['Image'] = img 

            uuid_str = self.generate_UUID()
            self.game_dict[f'{i}']['UUID'] = uuid_str

            name = self.get_game_title(soup)
            self.game_dict[f'{i}']['Name'] = name   

            dev_list = self.game_dev(soup)
            self.game_dict[f'{i}']['Developers'] = dev_list

            pub = self.game_pub(soup)
            self.game_dict[f'{i}']['Publisher'] = pub

            date = self.release_date(soup)
            self.game_dict[f'{i}']['Release_Date'] = date

            game_folder = self.game_dict[f'{i}']['Name']
            a_dict = self.game_dict[f'{i}']
            self.make_game_folder(game_folder, a_dict)

            self.save_image_file(game_folder, img)
            
    pass

if __name__ == "__main__":
    number_of_games = 20
    url = "https://store.steampowered.com/"
      
    scrape = Scraper(number_of_games, url)
