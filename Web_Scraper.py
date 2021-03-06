
import string
import requests
import uuid
import os
import shutil
import json
import urllib.request
import boto3
import mimetypes
import getpass 
import pandas as pd
import psycopg2
import chromedriver_autoinstaller
from bs4 import BeautifulSoup 
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from uuid import UUID 
from lxml import etree 
from sqlalchemy import create_engine
from tqdm import tqdm 

class Scraper:
    '''
        This class is for a Web scraper that will automatically collect data on the top selling games on Steam.

        It is populated with methods used to navigate the webpage, collect specific bits of information and then stores the information on a local json file. 
    '''
    def __init__(self, number_of_games: int, url: string,):

        chromedriver_autoinstaller.install()

        self._start_webdriver() # set up the headless mode options and start the webdriver

        self.number_of_games = number_of_games # number of games that will have their data collected

        self.URL = url # URL to the home page of the website

        self.unique_games_list = []

        self.s3_client = boto3.client('s3')

        self.bucket_name = 'arion-steam-scraper'

        self._make_folder()
        
        self._open_browser()
        
        sleep(5)
        self._cookie_button() #get rid of cookies pop up

        sleep(1)
        #self._go_to_top_seller() # go to the top sellers page

        sleep(1)

        self._filter_page()

        self.game_list = self._make_list_of_links(self.number_of_games) # List of links to the store page of the games

        self._close_browser()

        self.game_dict = self._make_dictionary(self.number_of_games) # Dictionary where the data for each game will be stored        

        self.create_bucket()

        #print(self.check_id(20))

        self._collect_data(self.number_of_games)        

        self.game_dict_to_rds()

        print("all done")

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
    
    def _start_webdriver(self):
        #this method is to set up the options for selenium headless mode

        options = Options()
        options.add_argument("--headless")
        options.add_argument("window-size=1920,1080")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-setuid-sandbox")

        self.driver = webdriver.Chrome(options=options)
        

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
        try:
            prod_id = fish['data-appid']
        except:
            prod_id = 1 
        return prod_id      

    def generate_UUID(self): 
        
        # generate an UUID for each game
        unique_id = uuid.uuid4()
        uuid_str = str(unique_id)

        return uuid_str        

    def get_cover_image(self, soup): 
        
        #gets the cover image of the game

        fish = soup.find(name='img', attrs={'class':'game_header_image_full'})
        try:
            img = fish['src']
        except: 
            img = "none"
        return img      
    
    def get_game_title(self, soup): 
        
        # gets the game's title

        fish = soup.find(name='div', attrs={'id':'appHubAppName', 'class':'apphub_AppName'})
        try:
            name = fish.text
        except:
            name = "none"

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
        
        try:
            fish_list = fish.find_all('a')
            dev_list = [elem.text for elem in fish_list]
        except:
            dev_list = []
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
        try:
            date = fish.text
        except:
            date = "none"

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
    
    def add_unique_games(self, prod_id):
        # this methid adds the unique id of each game to a list which will then be checked to avoid rescraping the same data
        self.unique_games_list.append(prod_id)
    
    def check_id(self, prod_id):
        # this method will check the rds database to see if the game has already been scraped before
        HOST = 'arionsteam.ck6kqnmgieka.eu-west-2.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = 'thiswillwork'
        DATABASE = 'postgres'
        PORT = 5432

        conn = psycopg2.connect(host= HOST, user= USER, password=PASSWORD, dbname=DATABASE, port=PORT)
        cur = conn.cursor()
        anumber = prod_id
        try:
            idthis = int(anumber)
        except:
            idthis = 1
        cur.execute("""SELECT EXISTS(SELECT * FROM steam_dataset WHERE "ID"='{}')""".format(idthis))
        res = cur.fetchall()
        if res == [(True,)]:
            return True
        else:
            return False

    def _collect_data(self, number):
        # This method runs all the methods for collecting data

        for i in tqdm(range(number)):
            store_page = self.game_list[i]
            soup = self.make_soup(store_page)

            prod_id = self.get_product_ID(soup)

            if prod_id in self.unique_games_list: # This is to check if the game has already been scraped 
                continue
            else:
                self.add_unique_games(prod_id)

            #This will check if the game already exists in the RDS database and if so, it won't be scraped 
            if self.check_id(prod_id) == True:
                 print("skipped")
                 continue
            
            
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

            self.upload_json_to_s3(game_folder)

            self.upload_img_to_s3(img, game_folder)
    
    def delete_folder(self):
        #Method used to delte folder for testing purposes 
        path = 'raw_data'
        shutil.rmtree(path)
        pass

    def create_bucket(self):
        # Method used to create bucket on AWS S3
        try:
            
            s3_location = {'LocationConstraint': 'eu-west-2'}

            self.s3_client.create_bucket(Bucket=self.bucket_name, CreateBucketConfiguration=s3_location)
        except:
            pass
        pass

    def upload_json_to_s3(self, game_folder):
        # Method to upload json data file to s3
        local_path = os.path.join(self.root_dir, self.raw_data_folder, game_folder, "data.json")
        s3_path = os.path.join(game_folder, "data.json")

        try:
            self.s3_client.upload_file(local_path, self.bucket_name, s3_path)
            
        except:
            pass

    
    def upload_img_to_s3(self, img, game_folder):
        # Method for uploading images to s3
        try:
            imageResponse = requests.get(img, stream=True).raw
            content_type = imageResponse.headers['content-type']
            extension = mimetypes.guess_extension(content_type)
            s3_img = os.path.join(game_folder, 'cover' + extension)
            self.s3_client.upload_fileobj(imageResponse, self.bucket_name, s3_img)
            
        except: 
            pass
    
    def create_pd_dataframe(self, a_dict):
        #Creates a pandas dataframe from a dictionay
        game_df = pd.DataFrame.from_dict(a_dict, orient='index') 
        
        return game_df

    def dataframe_to_rds(self, df):
        #Uploads a pandas dataframe to RDS
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'arionsteam.ck6kqnmgieka.eu-west-2.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = 'thiswillwork' # manually input password
        PORT = 5432
        DATABASE = 'postgres'
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        df.to_sql('steam_dataset', engine, if_exists='replace')

    def game_dict_to_rds(self):
        #Takes the dictionay containing all data collected and uploads to RDS
        game_df = self.create_pd_dataframe(self.game_dict)
        

        self.dataframe_to_rds(game_df) 
        


    pass

if __name__ == "__main__":
    number_of_games = 20
    #url = "https://store.steampowered.com/"

    url = "https://store.steampowered.com/search/?filter=topsellers"
      
    scrape = Scraper(number_of_games, url)
