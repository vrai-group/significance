from eBay import Site
#from mongo import Mongo
#from selenium.common.exceptions import TimeoutException

site = Site()
print("Website opened")
site.land_first_page()

#site.implicit_wait()
# try:
#     site.decline_cookies()
#     print("Cookies declined")
#     #site.accept_cookies()
#     #print("Cookies accepted")
# except:
#     print("no cookies")
# #site.implicit_wait()

itemUrls= site.getAllItemUrls()
site.getAllItem(itemUrls)
site.tearDown()
print("Website closed")

#print("Mongo connection")
#mongo = Mongo()
#mongo.upload_object()
#print("Close connection")
#mongo.close_connection()
