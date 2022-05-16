
import requests
import uuid
import os
import json
import urllib.request
from bs4 import BeautifulSoup 
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By



driver = webdriver.Chrome()

class Scraper:
    def __init__(self):
        self.make_folder()

        self.make_dictionary()

        self.URL = "https://store.steampowered.com/"

        driver.maximize_window()

        driver.get(self.URL)
        
        sleep(5)
        self.cookie_button() #get rid of cookies pop up

        # sleep(2)
        # self.scrolling()

        sleep(1)
        self.go_to_top_seller() # go to the top sellers page

        sleep(1)
        self.make_list_of_links()

        self.get_product_ID()

        self.get_cover_image()

        self.get_game_title()

        #self.generate_UUID()

        #print(self.game_dict2)

        self.make_game_folder()

        self.save_image_file()
        pass

    def make_folder(self):
        self.root_dir = os.path.dirname(os.path.abspath(__file__)) 
        self.raw_data_folder = 'raw_data'

        path = os.path.join(self.root_dir, self.raw_data_folder)
        try:
            os.mkdir(path)
        except:
            pass

    def go_to_top_seller(self):
        try:
            top_seller_link = driver.find_element(By.XPATH, '//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div[1]/div[8]/a[1]')
            top_seller_link.click()
        finally:
            pass

    def cookie_button(self):
        try:
            reject_cookie_button = driver.find_element(By.XPATH, '//*[@id="rejectAllButton"]')
            reject_cookie_button.click()
        except AttributeError:
            driver.switch_to('#cookiePrefPopup')
            reject_cookie_button = driver.find_element(By.XPATH, '//*[@id="rejectAllButton"]')
            reject_cookie_button.click()
        finally:
            pass
    
    def scrolling(self):
        driver.execute_script("window.scrollBy(0,2000)","")

    def make_dictionary(self):
        self.game_dict = {'id':[], 'uuid':[], 'name':[], 'image':[]}
        self.game_dict2 = {}
        pass

    def make_list_of_links(self): # makes a list of links of the top selling games which will then be parsed by other methods to extract data
        self.game_list = []
        #<span class="title">Steam Deck</span>  ignore steam deck
        #//*[@id="search_resultsRows"] all the items are this path's children 
        #first request the html of the page
        # this_URL = driver.current_url
        # this_page = requests.get(this_URL)
        # this_soup = BeautifulSoup(this_page.text, 'html.parser')

        

        button_filter_type = driver.find_element(By.XPATH, '//*[@id="additional_search_options"]/div[3]/div[1]')
        button_filter_type.click()

        sleep(2)

        

        button_filter_games = button_filter_type.find_element(By.XPATH, '//*[@id="narrow_category1"]/div[1]/span/span/span[2]') 
        button_filter_games.click()

        sleep(2)

        game_container = driver.find_element(By.XPATH, '//*[@id="search_resultsRows"]') # this container holds all the top games
        sleep(1)
        self.top_list = game_container.find_elements(By.XPATH, './a')
        sleep(1)
        #print(self.top_list)
        top_list_links = [elem.get_attribute('href') for elem in self.top_list] # this extracts the hyperlinks to the individual store page 
        for i in range(20):            
            self.game_list.append(top_list_links[i])
            self.game_dict2[f'{i}'] = {}
            pass
        #print(self.game_list)
        pass
    
    def get_product_ID(self): # generate a user friendly id unique to each product
        t = 0
        for i in self.game_list:
            page = requests.get(i)
            soup = BeautifulSoup(page.text, 'html.parser')
            fish = soup.find(name ='div', attrs={'class':"glance_tags popular_tags"})
            prod_id = fish['data-appid']
            self.game_dict['id'].append(prod_id)

            self.game_dict2[f'{t}']['ID'] = prod_id 


            t += 1
            #print(fish['data-appid'])

        
        pass

    def generate_UUID(self): # generate a unique ID for each product
        #THIS IS BROKEN, can't dump UUID to json files
        t = 0
        for i in self.game_list:
            unique_id = uuid.uuid4()
            self.game_dict['uuid'].append(unique_id)

            self.game_dict2[f'{t}']['UUID'] = unique_id

            t += 1


    def get_cover_image(self): #gets the cover image of the game
        t = 0
        for i in self.game_list:
            page = requests.get(i)
            soup = BeautifulSoup(page.text, 'html.parser')
            fish = soup.find(name='img', attrs={'class':'game_header_image_full'})
            img = fish['src']
            self.game_dict['image'].append(img)

            self.game_dict2[f'{t}']['Image'] = img

            t += 1
            #print(fish['src'])
        pass
    
    def get_game_title(self): # get's the game;s title
        t = 0
        for i in self.game_list:
            page = requests.get(i)
            soup = BeautifulSoup(page.text, 'html.parser')
            fish = soup.find(name='div', attrs={'id':'appHubAppName', 'class':'apphub_AppName'})
            name = fish.text
            self.game_dict['name'].append(name)

            self.game_dict2[f'{t}']['Name'] = name

            t += 1
            #print(fish.text)

    ## NOTETOSELF : get more details from each game page by creating more methods; number of reviews, tags, review avg, price etc

    def make_game_folder(self):
        #this method makes a folder for each game
        t = 0
        for i in self.game_list:
            try:
                game_folder = self.game_dict2[f'{t}']['Name']

                path = os.path.join(self.root_dir, self.raw_data_folder, game_folder)

                os.mkdir(path)

                dict = self.game_dict2[f'{t}']

                with open(f'{path}/data.json', 'w') as fp:
                    json.dump(dict, fp)

                t += 1
            except:
                t += 1
                pass
        #and also creats json file for each game's dictionary 
        pass

    def save_image_file(self):
        t = 0
        for i in self.game_list:
            try:
                game_folder = self.game_dict2[f'{t}']['Name']
                path = os.path.join(self.root_dir, self.raw_data_folder, game_folder, 'images')
                os.mkdir(path)

                urllib.request.urlretrieve(self.game_dict2[f'{t}']['Image'], f'{path}/1.jpg')

                t += 1
            except:
                t += 1
                pass
        pass


    pass

if __name__ == "__main__":
    scrape = Scraper()
