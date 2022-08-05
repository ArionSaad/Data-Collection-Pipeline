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
```

## Milestone 3

- Created methods to parse the unique Id for each product from the store page in addiion to generating an UUID4 for each.
- Created a number of methods which use BeautifulSoup to go through each link and collects various information about each product.
- Extracted data is stored in a dictionary which is easily converted to json file.
- Programmatically created indvidual folders for each product to store json file and any images downloaded from the store page.

```python
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
        
        for i in range(len(self.game_list)):
            try:
                game_folder = self.game_dict2[f'{i}']['Name']
                path = os.path.join(self.root_dir, self.raw_data_folder, game_folder, 'images')
                os.mkdir(path)

                urllib.request.urlretrieve(self.game_dict2[f'{i}']['Image'], f'{path}/1.jpg')

                
            except:
                
                pass
        pass
```

## Milestone 4

- Created a unit test file to test the public methods in the Scraper class.
- In order to make sure the web scraper was collecting the correct data from the store pages, a number of unit tests were written to validate the data collected.
- To optimize the code repeated for loops where coalesced into a single method with a single for loop. This made the code run much faster than before. 
```python 
import unittest
import requests
from selenium import webdriver
from Web_Scraper import Scraper
from bs4 import BeautifulSoup 
from lxml import etree 


class ScraperTestCase(unittest.TestCase):
    '''
        This is a unit test class for the web scraper.
    '''
    @classmethod
    def setUpClass(cls):
        
        pass

    @classmethod
    def tearDownClass(cls):
        
        pass

    def setUp(self):
        self.web_page = "https://store.steampowered.com/app/1245620/ELDEN_RING/"
        self.soup = Scraper.make_soup(self, self.web_page)
        pass

    def tearDown(self):
        pass
    
    def test_make_dictionary(self):
        
        expected_output = {'0': {}, '1': {}, '2': {}, '3': {}, '4': {}}
        actual_output = Scraper._make_dictionary(self, 5)
        self.assertEqual(expected_output, actual_output)

    def test_make_soup(self):
        
        page = requests.get(self.web_page)
        soup = BeautifulSoup(page.text, 'html.parser')
        expected_output = soup
        
        actual_output = Scraper.make_soup(self, self.web_page)

        self.assertEqual(type(expected_output), type(actual_output))

    def test_get_product_ID(self):
        fish = self.soup.find(name ='div', attrs={'class':"glance_tags popular_tags"})
        expected_output = fish['data-appid']

        actual_output = Scraper.get_product_ID(self, self.soup)

        self.assertEqual(expected_output, actual_output)

    def test_get_cover_image(self):
        fish = self.soup.find(name='img', attrs={'class':'game_header_image_full'})
        expected = fish['src']

        actual = Scraper.get_cover_image(self, self.soup)

        self.assertEqual(expected, actual)

    def test_game_dev(self):
        fish = self.soup.find(name='div' , attrs={'class':"summary column", 'id':'developers_list' })
        fish_list = fish.find_all('a')
        expected = [elem.text for elem in fish_list]

        actual = Scraper.game_dev(self, self.soup)

        self.assertEqual(expected, actual)

    def test_game_pub(self):
        fish = etree.HTML(str(self.soup))        
        expected = fish.xpath('//*[@id="game_highlights"]/div[1]/div/div[3]/div[4]/div[2]/a')[0].text     

        actual = Scraper.game_pub(self, self.soup)

        self.assertEqual(expected, actual)       
    
    def test_release_date(self):
        fish = self.soup.find(name='div', attrs={'class':'date'})
        expected = fish.text

        actual = Scraper.release_date(self, self.soup)

        self.assertEqual(expected, actual)

    def test_get_game_title(self):
        fish = self.soup.find(name='div', attrs={'id':'appHubAppName', 'class':'apphub_AppName'})
        expected = fish.text

        actual = Scraper.get_game_title(self, self.soup)

        self.assertEqual(expected, actual)     

    pass


unittest.main(argv=[''], verbosity=2, exit=False)
```

## Mileston 5

- Set up AWS cli and IAM user on AWS.
- Uplodad the data json files and images to the s3 data lake.
- Coverted all collected data into a daaframe and uploaded to AWS RDS.
- 
```python
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
        DATABASE = 'arion_steam_database'
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        df.to_sql('steam_dataset', engine, if_exists='replace')
```

## Milestone 6 

- Added a progress bar using tqdm package. 
- Added a method that will add the unique ID of each game to a list. This list will be checked to prevent the same game from being scraped again. 

## Milestone 7

- Modified the webdriver to run in headless mode.
- Created a docker image of scraper and uploaded to dockerhub.
- Created an EC2 instance to run the docker image on AWS.
- Created security group for EC2 with three inbound rules: 
- -- HTTP: Anywhere IPv4, 
- -- HTTPS: Anywhere IPv4, 
- -- SSH: My IP. 
- And 2 outbound rules:
- -- HTTP: Anywhere IPv4, 
- --HTTPS: Anywhere IPv4


