## EBay Crawler

The code for crawling from eBay is closed inside this directory that include code, chromedriver, configuration file.

First of all you have to set the “config_file.json” contains the configurable parameters. The most important parameters are:
- EBAY_DIRECT_URL which contains the eBay url to a page of results appropriately filtered through categories or text search with the commands of the web interface.
- OUT_FOLDER_PATH which contains the folder path where the images and the metadata of the individual products will be saved.

To run the crawler (after setting the configuration parameters), you need to run the command:
`python main.py`

The main python packages needed for work the code are:
- beautifulsoup4
- selenium
- requests

At the moment, the code has been structured to recover, from the individual products for sale on eBay, in addition to its image, information including:
- item URL
- image URL
- price
- bid price (for auction sale)
- seller
- seller followers
- seller feedback
- payment method
Furthermore, other auxiliary info are recorded:
- ID
- timestamp
- image flag ok (if the image file has been downloaded correctly)
