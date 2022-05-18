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

- Created a unit test file to test all the methods in the Scraper class.
