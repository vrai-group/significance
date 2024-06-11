from datetime import datetime
import time
import unittest
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
import json
import os
import requests

with open('config_file.json') as config_file:
    config = json.load(config_file)
    current_website = "EBAY"


if not os.path.exists(config['OUT_FOLDER_PATH']):
    os.makedirs(config['OUT_FOLDER_PATH'])

# DOWNLOAD IMAGE
def download_img(imageUrl, imageSavePath):
    # Download the track
    try:
        r = requests.get(imageUrl, allow_redirects=True)
        with open(imageSavePath, 'wb') as f:
            f.write(r.content)
        flag = False
    except:
        flag = True

    # Print to the console to keep track of how the scraping is coming along.
    # print('Downloaded: {}'.format(id))
    return flag


class Site(unittest.TestCase):

    def __init__(self):
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # To avoid notification popup
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        #options.add_argument("window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument('--disable-blink-features=AutomationControlled')
        #options.add_argument("--headless")
        # Pass the argument 1 to allow and 2 to block
        options.add_experimental_option("prefs", { 
            "profile.default_content_setting_values.notifications": 1 
        })
        s = Service(config['CHROME_PATH'])
        #s = Service(os.path.abspath(config['CHROME_PATH']))
        self.driver = webdriver.Chrome(service=s, options=options)
        self.source = self.driver.page_source
        self.soup = BeautifulSoup(self.source, "html.parser")
        super(Site, self).__init__()
        global wait
        wait = WebDriverWait(self.driver, 5)
        

    def land_first_page(self):
        self.driver.get(config['URL_DIRETTO_'+ current_website])
        self.driver.maximize_window()
        global start_window
        start_window = self.driver.window_handles[0]

    def land_item_page(self,url):
        self.driver.get(url)
        item_window = self.driver.window_handles[0]
        self.driver.switch_to.window(item_window)

    def implicit_wait(self):
        self.driver.implicitly_wait(5)
    
    def accept_cookies(self):
        element = self.driver.find_element(By.ID, config['COOKIES_ACCEPT_ID_' + current_website])
        self.driver.execute_script("arguments[0].click();", element)

    def decline_cookies(self):
        element = self.driver.find_element(By.ID, config['COOKIES_DECLINE_ID_' + current_website])
        self.driver.execute_script("arguments[0].click();", element)
            
    def tearDown(self):
        self.driver.switch_to.window(start_window)
        self.driver.close()

    # GET ALL ITEM URL
    def getAllItemUrls(self):
        pageRows = 60
        totalItem = int(self.driver.find_element(By.XPATH,"//*[@id='mainContent']/div[1]/div/div[2]/div[1]/div[1]/h1/span[1]").text.replace('.', ''))
        totalPage= totalItem//pageRows
        itemUrls=[]

        for p in range(1,totalPage+1): #[:3]: ###
            print("Page " + str(p))

            self.land_item_page(config['URL_DIRETTO_'+ current_website]+"&_pgn={}".format(p))

            for i in range(1,pageRows+1): #[:10]: ###
                itemUrl = self.driver.find_element(By.XPATH, "//*[@id='srp-river-results']/ul/li[%s]/div/div[2]/a"%(i+1)).get_attribute("href")
                itemUrls.append(itemUrl)

        itemUrls= list(set(itemUrls))
        return itemUrls

    # GET ALL ITEM
    def getAllItem(self, itemUrls):

        itemsList=[]

        for i, itemUrl in enumerate(itemUrls): ###

            print("Item {} - {} ".format(i, itemUrl))
            self.land_item_page(itemUrl)
            itemDict = {}

            imageUrl = self.driver.find_element(By.XPATH,"//*[@id='mainImgHldr']/div[1]/div/div/img").get_attribute("src")
            imageUrlSplitted= imageUrl.split("/")
            imageExt= os.path.splitext(imageUrlSplitted[-1])[-1]
            imageUrlSplitted[-1]= "s-l2000" + imageExt
            ID= imageUrlSplitted[-2]
            imageUrl= "/".join(imageUrlSplitted)
            itemDict["ID"]= ID
            itemDict["timestamp"] = time.time()
            itemDict["itemUrl"] = itemUrl
            itemDict["imageUrl"]= imageUrl

            try:
                title = self.driver.find_element(By.XPATH,"//*[@id='LeftSummaryPanel']/div[1]/div[1]/div/h1/span").text
                itemDict["title"] = title
            except:
                None
            try:
                price = self.driver.find_element(By.XPATH, "//*[@id='prcIsum']").text
                itemDict["price"] = price
            except:
                None
            try:
                bidPrice = self.driver.find_element(By.XPATH, "//*[@id='prcIsum_bidPrice']").text
                itemDict["bidPrice"] = bidPrice
            except:
                None
            try:
                seller = self.driver.find_element(By.XPATH, "//*[@id='RightSummaryPanel']/div[3]/div[1]/div/div[2]/div/div[1]/div/a[1]/span").text
                itemDict["seller"] = seller
            except:
                None
            try:
                sellerScore = self.driver.find_element(By.XPATH, "//*[@id='RightSummaryPanel']/div[3]/div[1]/div/div[2]/div/div[1]/div/a[2]/span").text
                itemDict["sellerScore"] = sellerScore
            except:
                None
            try:
                sellerPositiveFeedback = self.driver.find_element(By.XPATH, "//*[@id='RightSummaryPanel']/div[3]/div[1]/div/div[2]/div/div[2]/span").text
                itemDict["sellerPositiveFeedback"] = sellerPositiveFeedback
            except:
                None

            payments= []
            spr = self.driver.find_element(By.XPATH, "//*[@id='SRPSection']")
            try:
                spr.find_element(By.CLASS_NAME, "ux-textspans--PAYPAL")
                payments.append("PAYPAL")
            except:
                None
            try:
                spr.find_element(By.CLASS_NAME, "ux-textspans--GOOGLE_PAY")
                payments.append("GOOGLE_PAY")
            except:
                None
            try:
                spr.find_element(By.CLASS_NAME, "ux-textspans--VISA")
                payments.append("VISA")
            except:
                None
            try:
                spr.find_element(By.CLASS_NAME, "ux-textspans--MASTER_CARD")
                payments.append("MASTER_CARD")
            except:
                None
            try:
                spr.find_element(By.CLASS_NAME, "ux-textspans--AM_EX")
                payments.append("AM_EX")
            except:
                None
            try:
                spr.find_element(By.CLASS_NAME, "ux-textspans--DISCOVER")
                payments.append("DISCOVER")
            except:
                None
            itemDict["payments"] = payments

            ### download image
            downloadErr= download_img(imageUrl, os.path.join(config['OUT_FOLDER_PATH'],"{}{}".format(ID,imageExt)))
            itemDict["imgOk"] = not(downloadErr)

            ### single metadata file json
            with open(os.path.join(config['OUT_FOLDER_PATH'],"{}.json".format(ID)), "w") as outfile:
                json.dump(itemDict, outfile)

            itemsList.append(itemDict)

        with open(os.path.join(config['OUT_FOLDER_PATH'],"allSamples.json"), "w") as outfile:
            # json.dump(dictionary, outfile, indent = 4)
            json.dump(itemsList, outfile)
