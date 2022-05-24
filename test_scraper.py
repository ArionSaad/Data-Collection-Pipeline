from Web_Scraper import Scraper
import unittest
import bs4


class ScraperTestCase(unittest.TestCase):
    '''
        This is a unit test class for the web scraper.
    '''
    def setUp(self):
        self.game_list = ['https://store.steampowered.com/app/1245620/ELDEN_RING/']
        self.make_soup = Scraper.make_soup(self, 0)
        

    def test_make_soup(self):
        expected_output = bs4.BeautifulSoup
        actual_output = self.make_soup()
        self.assertIsInstance(expected_output, actual_output)

    def tearDown(self):
        del self.game_list
        del self.make_soup
        
    pass


unittest.main(argv=[''], verbosity=2, exit=False)