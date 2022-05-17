
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

        sleep(1)
        self.go_to_top_seller() # go to the top sellers page

        sleep(1)
        self.make_list_of_links()

        self.get_product_ID()

        self.get_cover_image()

        self.get_game_title()

        self.generate_UUID()

        self.game_dev()
        
        self.game_pub()

        self.release_date()

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

        button_filter_type = driver.find_element(By.XPATH, '//*[@id="additional_search_options"]/div[3]/div[1]')
        button_filter_type.click()

        sleep(2)
        
        button_filter_games = button_filter_type.find_element(By.XPATH, '//*[@id="narrow_category1"]/div[1]/span/span/span[2]') 
        button_filter_games.click()

        sleep(2)

        game_container = driver.find_element(By.XPATH, '//*[@id="search_resultsRows"]') # this container holds all the top games
        sleep(1)
        top_list = game_container.find_elements(By.XPATH, './a')
        sleep(1)
        #print(self.top_list)
        top_list_links = [elem.get_attribute('href') for elem in top_list] # this extracts the hyperlinks to the individual store page 

        for i in range(20):  # select the top 20 games on the list          
            self.game_list.append(top_list_links[i])
            self.game_dict2[f'{i}'] = {}
            pass
        pass
    
    def get_product_ID(self): # generate a user friendly id unique to each product
        
        for i in range(len(self.game_list)):
            page = requests.get(self.game_list[i])
            soup = BeautifulSoup(page.text, 'html.parser')
            fish = soup.find(name ='div', attrs={'class':"glance_tags popular_tags"})
            prod_id = fish['data-appid']
            self.game_dict['id'].append(prod_id)

            self.game_dict2[f'{i}']['ID'] = prod_id 
            
            #print(fish['data-appid'])

        
        pass

    def generate_UUID(self): # generate a unique ID for each product
        
        
        for i in range(len(self.game_list)):
            unique_id = uuid.uuid4()

            uuid_str = str(unique_id)

            self.game_dict['uuid'].append(uuid_str)

            self.game_dict2[f'{i}']['UUID'] = uuid_str

            


    def get_cover_image(self): #gets the cover image of the game
        
        for i in range(len(self.game_list)):
            page = requests.get(self.game_list[i])
            soup = BeautifulSoup(page.text, 'html.parser')
            fish = soup.find(name='img', attrs={'class':'game_header_image_full'})
            img = fish['src']

            self.game_dict['image'].append(img)

            self.game_dict2[f'{i}']['Image'] = img          
            
        pass
    
    def get_game_title(self): # gets the game's title
        
        for i in range(len(self.game_list)):
            page = requests.get(self.game_list[i])
            soup = BeautifulSoup(page.text, 'html.parser')
            fish = soup.find(name='div', attrs={'id':'appHubAppName', 'class':'apphub_AppName'})
            name = fish.text

            self.game_dict['name'].append(name)

            self.game_dict2[f'{i}']['Name'] = name            
            

    ## NOTETOSELF : get more details from each game page by creating more methods; number of reviews, tags, review avg, price etc   

    def get_game_tags(self):
        ## BROKEN
        for i in range(len(self.game_list)):
            page = requests.get(self.game_list[i])
            soup = BeautifulSoup(page.text, 'html.parser')
            fish =soup.find(name='div' , attrs={'class':"glance_tags popular_tags" })
            tag_list_html = fish.find_all('a')
            tag_list = [elem.text for elem in tag_list_html]
            self.game_dict2[f'{i}']['Tags'] = tag_list

    def game_dev(self):
        for i in range(len(self.game_list)):
            page = requests.get(self.game_list[i])
            soup = BeautifulSoup(page.text, 'html.parser')
            fish =soup.find(name='div' , attrs={'class':"summary column", 'id':'developers_list' })
            fish_list = fish.find_all('a')
            dev_list = [elem.text for elem in fish_list]
            
            self.game_dict2[f'{i}']['Developers'] = dev_list

    def game_pub(self):
        for i in range(len(self.game_list)):
            page = requests.get(self.game_list[i])
            soup = BeautifulSoup(page.text, 'html.parser')
            fish = etree.HTML(str(soup))
            try:
                pub = fish.xpath('//*[@id="game_highlights"]/div[1]/div/div[3]/div[4]/div[2]/a')[0].text
                
                self.game_dict2[f'{i}']['Publisher'] = pub
            except: 
                pass

    def release_date(self):
        for i in range(len(self.game_list)):
            page = requests.get(self.game_list[i])
            soup = BeautifulSoup(page.text, 'html.parser')
            fish = soup.find(name='div', attrs={'class':'date'})
            date = fish.text

            self.game_dict2[f'{i}']['Release_Date'] = date
											


    def make_game_folder(self):
        #this method makes a folder for each game
        
        for i in range(len(self.game_list)):
            try:
                game_folder = self.game_dict2[f'{i}']['Name']

                path = os.path.join(self.root_dir, self.raw_data_folder, game_folder)

                os.mkdir(path)

                dict = self.game_dict2[f'{i}']

                with open(f'{path}/data.json', 'w') as fp:
                    json.dump(dict, fp)

                
            except:
                
                pass
        #and also creats json file for each game's dictionary 
        pass

    def save_image_file(self):
        t = 0
        for i in range(len(self.game_list)):
            try:
                game_folder = self.game_dict2[f'{i}']['Name']
                path = os.path.join(self.root_dir, self.raw_data_folder, game_folder, 'images')
                os.mkdir(path)

                urllib.request.urlretrieve(self.game_dict2[f'{i}']['Image'], f'{path}/1.jpg')

                
            except:
                
                pass
        pass


    pass

if __name__ == "__main__":
    scrape = Scraper()
