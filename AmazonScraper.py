import asyncio, aiohttp, nest_asyncio, random
from bs4 import BeautifulSoup as BeautifulSoup

class AmazonScraper:

    def __init__(self) -> None:
        self.base_url='https://www.amazon.com'
        self.page = ''

    def get_product(self, asin:str):
        """None
           This method is to get the product page either by asin

            Args:
                asin (str): Takes the asin or the product id of the getting the product.
            
            Retrun:
                dict: Returns the data as dictionary.
        """
        
        pass

    def _getAsin(self, page=None):
        """
            The method scrapes asin(amazon product id) from the page.
        """

        pass