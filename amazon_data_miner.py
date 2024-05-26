# -*- coding: utf-8 -*-
"""AMAZON DATA MINER

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ys42Alx_8c9OF2DOI459kYiGTwevfeBe
"""

!pip install aiohttp
!pip install nest_asyncio

pip list

import re, os, json, time, requests
import aiohttp
import nest_asyncio
from bs4 import BeautifulSoup as BeautifulSoup
import asyncio

class file_handle():
  def write_in(self, file_name : str,data):
      file = open(file_name,'a')
      ttype = type(data)
      if ttype ==  str:
          file.write(data)
          file.write(',')
      elif ttype == dict:
          json.dump(data,file)
          file.write(';')
      elif ttype == list or ttype == tuple or ttype == set:
          for d in data:
              file.write(d)
              file.write(',')
      file.close()

  def write_file(self, file_name : str,data):
      file = open(file_name,'w')
      ttype = type(data)
      if ttype ==  str:
          file.write(data)
          file.write(',')
      elif ttype == dict:
          json.dump(data,file)
          file.write(';')
      elif ttype == list or ttype == tuple or ttype == set:
          for d in data:
              file.write(d)
              file.write(',')
      file.close()

  def read_file(self, file_name : str, spliter = None):
      file = open(file_name,'r',encoding='utf-8',errors='ignore')
      data = file.read()
      if spliter != None:
          data = data.split(spliter)
      file.close()
      return data

file_handle = file_handle()

class AmazonScrape():

    def __init__(self):

        file_loca = '/content/drive/MyDrive/Colab Notebooks/storage'     #location where all the files are stored
        self.file_asinList = file_loca + '/asinList.txt'
        self.file_product_url = file_loca + '/productUrls.txt'
        self.file_product_Data = file_loca + '/product_data.json'
        self.file_pagination_Data = file_loca + '/pagination_list.json'
        self.file_searched_products = file_loca + '/search_data.json'
        self.file_searchPage_List = file_loca + '/searchKeywords.txt'
        self.file_searchedList = file_loca + '/searchedList.txt'

        # gets all user agents and coverts the list into set for efficiency
        self.user_agents = set(file_handle.read_file(file_loca+'/user-agent.txt',"\n"))
        print('user_agents total:' + str( len(self.user_agents) ))

        # list of proxies
        self.proxy = set(file_handle.read_file(file_loca+'/proxies.txt',"\n"))
        print('Proxies total:' + str( len(self.proxy) ))

        # gets all the queries for searching
        self.search_keys = set(file_handle.read_file(self.file_searchPage_List,','))
        print('search_keys total:' + str( len(self.search_keys) ))

        # gets all the urls the have been scraped
        self.searchedUrls = set(file_handle.read_file(self.file_searchedList,','))
        print('searchedUrls total:' + str( len(self.searchedUrls) ))

        # gets all the asins that have been scraped
        self.asin_found = set(file_handle.read_file(self.file_asinList,','))
        print('asin_found total:' + str( len(self.asin_found) ))

    async def getall_searchdata(self, url, pg):
        # links = []
        products = pg.select('div[data-asin]')
        for product in products:
            asin = product.get('data-asin')
            if asin != '':
                if asin not in self.asin_found:

                    title = ''
                    price = ''
                    link = ''
                    rating_link = ''
                    rating_no = ''
                    img = ''
                    alt = ''
                    srcset = ''
                    choices_price = ''
                    choices_link = ''

                    if product.select('div.sg-col-4-of-12.sg-col-8-of-16.sg-col-12-of-20.sg-col div div:nth-child(1) div div div:nth-child(1) h2 a span'):
                        title = product.select('div.sg-col-4-of-12.sg-col-8-of-16.sg-col-12-of-20.sg-col div div:nth-child(1) div div div:nth-child(1) h2 a span')[0].text
                        self.asin_found.add(asin)
                        file_handle.write_in(self.file_asinList,str(asin))

                        if product.select('div.sg-col-4-of-12.sg-col-4-of-16.sg-col.sg-col-4-of-20 div div.a-section.a-spacing-none.a-spacing-top-small div div div a span[data-a-size=l] span.a-offscreen'):
                            price = product.select('div.sg-col-4-of-12.sg-col-4-of-16.sg-col.sg-col-4-of-20 div div.a-section.a-spacing-none.a-spacing-top-small div div div a span[data-a-size=l] span.a-offscreen')[0].text

                        if product.select('div.sg-col-4-of-12.sg-col-4-of-16.sg-col.sg-col-4-of-20 div div span a'):
                            imageLinks = product.select('div.sg-col-4-of-12.sg-col-4-of-16.sg-col.sg-col-4-of-20 div div span a')[0]
                            if imageLinks != '':
                                if imageLinks.select('div img.s-image'):
                                    images = imageLinks.select('div img.s-image')[0]
                                    if images.get('srcset'):
                                        srcset = images.get('srcset')
                                    if images.get('src'):
                                        img = images.get('src')
                                    if images.get('alt'):
                                        alt = images.get('alt')

                        if product.select('div.sg-col-4-of-12.sg-col-8-of-16.sg-col-12-of-20.sg-col div div:nth-child(1) div div div:nth-child(1) h2 a'):
                            link = 'https://www.amazon.com'+ product.select('div.sg-col-4-of-12.sg-col-8-of-16.sg-col-12-of-20.sg-col div div:nth-child(1) div div div:nth-child(1) h2 a')[0].get('href')

                        if product.select('div.sg-col-4-of-12.sg-col-8-of-16.sg-col-12-of-20.sg-col div div:nth-child(1) div div div.a-section.a-spacing-none.a-spacing-top-micro div span:nth-child(2) a'):
                            rting = product.select('div.sg-col-4-of-12.sg-col-8-of-16.sg-col-12-of-20.sg-col div div:nth-child(1) div div div.a-section.a-spacing-none.a-spacing-top-micro div span:nth-child(2) a')[0]
                            if rting:
                                rating_link = 'https://www.amazon.com'+rting.get('href')
                            if rting.select('span.a-size-base'):
                                rating_no = rting.select('span.a-size-base')[0].text

                        if product.select('div span div div div:nth-child(2) div.sg-col-4-of-12.sg-col-8-of-16.sg-col-12-of-20.sg-col div div:nth-child(2) div.sg-col-4-of-12.sg-col-4-of-16.sg-col.sg-col-4-of-20 div div.a-section.a-spacing-none.a-spacing-top-mini div'):
                            more_choice = product.select('div span div div div:nth-child(2) div.sg-col-4-of-12.sg-col-8-of-16.sg-col-12-of-20.sg-col div div:nth-child(2) div.sg-col-4-of-12.sg-col-4-of-16.sg-col.sg-col-4-of-20 div div.a-section.a-spacing-none.a-spacing-top-mini div')[0]
                            if more_choice != '':
                                if more_choice.select('span.a-color-base')[0]:
                                    choices_price = more_choice.select('span.a-color-base')[0].text
                                if more_choice.select('span.a-declarative a')[0]:
                                    choices_link = 'https://www.amazon.com'+more_choice.select('span.a-declarative a')[0].get('href')

                        data = {'ref':url,'asin':asin,'title':title,'price':price,'link':link,'ratings':{'rating_link':rating_link,'rating_no' : rating_no},'images':{'img':img, 'alt':alt, 'srcset':srcset},'more_choices':{'price':choices_price,'link':choices_link},}
                        # links.append(link)
                        file_handle.write_in(self.file_searched_products,data)

        # await self.asyTasks(self.urlManager, *links)

    async def asyTasks(self, func, *args):
        tasks = []
        for e in args:
            if e != '':
                tasks.append(loop.create_task(func(e)))
        if len(tasks) > 0:
            await asyncio.wait(tasks)

    async def pagination(self,pg):
        pagination = pg.select('ul.a-pagination li.a-last')
        paginations_list = []

        if pagination:
            pagesAvai = pg.select('ul.a-pagination li.a-disabled')[2].text
            linext = pg.select('ul.a-pagination li.a-normal')[0]
            linexts = linext.select('a')[0].get('href')
            for i in range(2,int(pagesAvai) + 1):
                pageLink = linexts.replace('page=2', f"page={i}")
                pageLink = 'https://www.amazon.com/s?k='+pageLink.replace('sr_pg_2',f"sr_pg_{i}")
                paginations_list.append(pageLink)

        await self.asyTasks(self.urlManager, *paginations_list)

    async def getProxies(self, proxy=None, port=None):
        print('proxies')

        if port == NoneBut isn't:
            port = random.randint(1, 9999)

        if proxy == None:
            num = random.randint(0, len(self.proxy))
            pox = list(self.proxy)
            proxy = pox[num]
            https = 'https://'+str(proxy)
            http = 'http://'+str(proxy)

        else :
            https = 'https://'+str(proxy) +':'+ str(port)
            http = 'http://'+str(proxy) +':'+ str(port)

        proxies = {
            'https':https,
            'http':http,
        }
        return proxies

    async def getHeaders(self, reffer = None):
        print('Headers')
        if reffer == None:
            da = random.randint(1,10)
            if (da % 2) == 0:
                ref = self.searchedUrls[random.randint(0, len(self.searchedUrls))]
            else:
                ref = 'https://www.amazon.com'
        else:
            ref = reffer

        num = len(self.user_agents)
        posi = random.randint(1, num)
        age = list(self.user_agents)
        agentUse =  age[posi]
        headers = {
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': agentUse,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': ref,
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }
        age = None
        return headers

    async def urlManager(self, link):
        url = ''
        typeUrl = ''

        modem = 'https://'
        text = 'www.amazon.com'

        searchType = '/s?k='
        searchType2 = 'node='
        productType = '/dp/B'
        productType2 = '/gp/'

        commentType = '#customerReviews'

        paginationType = 'page='
        paginationTtype2 = 'sr_pg_'


        if modem in link:
            if text in link:
                if paginationType in link and paginationTtype2 in link :
                    url = link
                    typeUrl = 'pagination'

                elif searchType in link or searchType2 in link:
                    typeUrl= 'search'
                    url = link

                elif commentType in link:
                    typeUrl = 'comment'
                    url = link

                elif productType2 in link or productType in link:
                    typeUrl = 'product'
                    url = link
        else:
            if re.search("B[0-9A-Z]+", link):
                url = modem + text +'/dp/'+link
                typeUrl = 'product'

            elif re.search("[A-Za-z0-9 ]+", link):
                url = modem+text+searchType+link
                typeUrl = 'search'

        if url not in self.searchedUrls:
            # print(url,typeUrl)
            await self.requestsPage(url,typeUrl)

    async def requestsPage(self, url, url_type):

        s = requests.Session()
        header = await self.getHeaders(url_type)
        proxy = await self.getProxies()
        r = s.get(url, headers=header)
        if r.status_code == 200:
            self.searchedUrls.add(url)
            file_handle.write_in(self.file_searchedList, url)

            pg = BeautifulSoup(r.text, 'html.parser')
            if pg != '':
                if url_type == 'search':
                    await self.getall_searchdata(url,pg)
                    await self.pagination(pg)

                elif url_type == 'pagination':
                    await self.getall_searchdata(pg)

                elif url_type == 'product':
                    await self.productScraper(pg)

                elif url_type == 'comment':
                    await self.commentScraper(pg)
        else:
            pass

    async def main(self, *urls):
        tasks = []
        if len(urls) > 0:
            if len(urls) > 1:
                for url in urls:
                    tasks.append(str(url))
            elif len(urls) == 1:
                tasks.append(str(urls[0]))
        await self.asyTasks(self.urlManager, *tasks)

start = time.time()
print(f' Started at {start}')
url = 'https://www.amazon.com/s?k=mouse+and+keyboards'

loop = asyncio.get_event_loop()
scraper = AmazonScrape()
loop.run_until_complete(scraper.main(url))
loop.close()
end = time.time()
print(f"time taken to execute is {end - start}")

# loop.stop()