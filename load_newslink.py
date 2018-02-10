from nutr.models import NewsLink,POC
from datetime import datetime
import os, requests,csv,sys
##################################
COUNTRYY = os.environ["COUNTRYY"]
filename = "news_"+COUNTRYY+".csv"
##################################
os.environ['DJANGO_SETTINGS_MODULE'] = 'epa7658577.settings'
from epa7658577 import settings
url = "http://search.yahoo.com/search?p=%s"
query = "python"
r = requests.get(url % query) 



def process_word(url, id):
        newslink=NewsLink()
        try:
            newslink.link=url.lower()
            newslink.title=url.lower()
            print("link set")
            poc=POC.objects.get(id=id)
            print("located POC object: ",poc.slug)
            newslink.poc=poc
            print("id set")
        except:
            e = sys.exc_info()[0]
            print('Error: ',e)
        try:
            newslink.save()
        except:
            e = sys.exc_info()[0]
            print('Error: ',e)



print("filename: ",filename)
if 'Users' in (os.environ['HOME']): #localhost
  path = "/Users/michaelsweeney/epa7658577/"+filename
else: #heroku
  path = "/app/"+filename
print("path: ",path)
dataReader = csv.reader(open(path), delimiter=',', quotechar='"')
for row in dataReader:
    url=row[0][:]
    id=row[1][:]
    process_word(url,id)

"""
soup = BeautifulSoup(r.text,"lxml")
soup.find_all(attrs={"class": "yschttl"})

for link in soup.find_all(attrs={"class": "yschttl"}):
    print ("%s (%s)" %(link.text, link.get('href')))
"""
