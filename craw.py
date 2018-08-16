import urllib.request
import urllib.parse
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId
"""""""""""""""
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
values = {
          'act' : 'login',
          'login[email]' : 'yzhang@i9i8.com',
          'login[password]' : '123456'
         }

data = urllib.parse.urlencode(values)
req = urllib.request.Request(url, data)
req.add_header('Referer', 'http://www.python.org/')
https://ithelp.ithome.com.tw/articles/10191408
"""""""""""""""
conn = MongoClient() ;
db = conn.craw
collection = db.NBA
class handleHtml :
    def __init__(self , html , boardName):
        self.boardName = boardName
        self.html = BeautifulSoup(html, 'html.parser')
        self.domainURL = "https://www.ptt.cc"
        try:
            data = self.parseAlldata()
            #將此頁資料存入NOSQL
            collection.insert_many(data)
        except Exception as e:
            print('Error to get page' + str(e))


        try:
            # 準備下一頁 非內容
            preLink = self.domainURL+self.nextPage()[3].get("href")
            preContent = get_web_page(preLink)
            print("go next : %s" %(preLink))
            handleHtml(preContent , self.boardName)
        except Exception as e:
            print('Error to get pre page' + str(e))
    def nextPage(self):
        next = self.html.find_all("a" , {"class":"btn"})
        return next
    def parseAlldata(self):
        #parse title
        all = []
        index = self.html.find_all(href=re.compile("\/bbs\/%s\/M." %(self.boardName)))
        for content in index:
            #尋找每一篇文章
            try:
                content_link = self.domainURL+content["href"];
                #print(content_link)
                pageContent = self.parseContentFromNextLink(content_link)

                c = re.match("(.*)\[(.*?)\](.*)", content.string)
                type = c.group(2)
                title = c.group(3)
                d = {
                    "type": type,
                    "title": title,
                    "content":pageContent,
                    "authur":pageContent["author"]
                }
                all.append(d)
            except Exception as e:
                print('Error to get content ' + str(e))
        return all
    def parseContentFromNextLink(self , contentURL):
        #parse ptt content 文章主體
        html = get_web_page(contentURL)
        parseContent = BeautifulSoup(html, 'html.parser')
        #article timestamp
        article = parseContent.findAll("span",{"class":"article-meta-value"})
        author = article[0].string
        articleTimestamp = article[3].string

        #push man
        push = []
        pushContent = parseContent.findAll("div",{"class":"push"})
        for p in pushContent:
            d={
                "pushTag":p.find("span" ,{"class","push-tag"}).string,
                "pushUserid":p.find("span", {"class", "push-userid"}).string,
                "pushContent":p.find("span", {"class", "push-content"}).string,
                "pushTimestamp":p.find("span", {"class", "push-ipdatetime"}).string.replace("\n" , "")
            }
            push.append(d)
        r = {
            "author":author,
            "articleTimestamp":articleTimestamp,
            "push":push
        }
        return r ;

def get_web_page(address):
    try:
        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        req = urllib.request.Request(address, headers=hdr)
        response = urllib.request.urlopen(req)
        the_page = response.read()
        try:
            return the_page
        finally:
            response.close()
    except Exception as e:
        print('Error to get page' + str(e) + address)

boardName = "NBA"
firstHtml = get_web_page('https://www.ptt.cc/bbs/%s/index.html' %(boardName))
page = handleHtml(firstHtml , "%s" %(boardName));
#preLink = page.nextPage()[2].string
#print("preLink %s" %(preLink))
