
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