'''
Created on Feb 9, 2010

@author: kbandla
'''
import urllib
import feedparser
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
from PageParser import PageParser

URL_TRENDS = "http://www.google.com/trends/hottrends?"
URL_VIZ_GRAPH = "http://www.google.com/trends/viz?"
URL_RSS = "http://www.google.com/trends/hottrends/atom/hourly"

class pytrends():
    
    def __init__(self):
        pass

    def __clean_date__(self,date):
        """Google Trends uses int-based date"""
        tmp = []
        for x in  date.split('-'):
            tmp.append(str((int(x))))
        return '-'.join(tmp)
    
    def trends_by_date(self,date):
        """Returns a list of Google Trends Keywords by Date. Returns False on Error"""
        args = {'sa':'X',
                'date':self.__clean_date__(date)
                }
        q = urllib.urlencode(args)
        html = ''
        try:
            html = urllib.urlopen(URL_TRENDS+q).read()
        except Exception,e:
            return False
        x = PageParser()
        x.feed(html)
        keywords = []
        for href in  x.hrefs:
            if '/trends/hottrends?q=' in href:
                url =  urlparse( 'http://www.google.com/'+href )
                params = dict([part.split('=') for part in url[4].split('&')])
                for k,v in params.items():
                    params[k] = v.replace('+',' ')
                keywords.append(params['q'])
        return keywords

    def trends_current(self):
        """Returns a list of current Google Trends Keywords"""
        d = feedparser.parse(URL_RSS)
        data = d['entries'][0]['content'][0]['value']
        soup = BeautifulSoup(data)
        trends = []
        for x in soup.findAll('a'):
            trends.add( x.contents[0] )
        return trends
    
    def trends_graph(self,query,date):
        """Returns a url string to a graph of the keyword. Returns False on any error"""
        args = {'hl':'',
                'q':query,
                'date':self.__clean_date__(date),
                'graph':'hot_img',
                'sa':'X'}
        q = urllib.urlencode(args)
        return URL_VIZ_GRAPH+q
    
if __name__ == "__main__":
    x = pytrends()
    print x.trends_by_date('2009-1-1')
    print x.trends_graph('craig ferguson twitter', '2010-02-08')
