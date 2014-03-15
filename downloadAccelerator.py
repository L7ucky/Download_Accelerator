import argparse
import sys
import threading
import requests
import urllib2
import math
from datetime import*
import time

class downloader(object):
	def __init__(self,URL,numThreads):
		self.numThreads= numThreads
		self.url= URL
		self.req= requests.head(self.url)
		self.size=int(self.req.headers['content-length'])
		self.subSize=math.ceil(self.size/float(self.numThreads))
		self.subSize=int(self.subSize)
		
		
	def get_content_part(self, position):
		if(position+1==self.numThreads):
			end= ((position+1)*self.subSize)+1
		else:	
			end= (position+1)*self.subSize
		if position==0:
			start=0
		else:
			start=end-(self.subSize-1)
		headers={'Range':'bytes=%s-%s' % (start,end)}
		r = requests.get(self.url, headers=headers)
		return r.content

class Shared(object):
    """ Shared memory """
    def __init__(self, d):
        self.d=d
        self.dictionary=dict()

        self.sem = threading.Semaphore()
        self.lock = threading.Lock()

        
    def addParts(self, index, peice):
		self.sem.acquire()
		self.dictionary[index]=peice
		self.sem.release()
		
class download(threading.Thread):
    """ A thread that increments and prints both a local and shared
    variable """
    def __init__(self,shared,dictKey):
        threading.Thread.__init__(self)
        self.dictKey = dictKey
        self.shared = shared
       
        

    def run(self):
		data=self.shared.d.get_content_part(self.dictKey)
		self.shared.addParts(self.dictKey,data)


def parse_options():
        parser = argparse.ArgumentParser(prog='threadHello', description='Simple demonstration of threading', add_help=True)
        parser.add_argument('-n', '--number', type=int, action='store', help='Specify the number of threads to create',default=10)
        parser.add_argument("URL",type=str, action='store', help= 'The Url provided', default= 'http://www.python.org/')
        return parser.parse_args()

if __name__ == "__main__":
    args = parse_options()
    d=downloader(args.URL, args.number)
    s = Shared(d)
    stringData=''
    threadsList= list()
    tstart = datetime.now()
    for i in range(0,args.number):
		
       h = download(s,i)
       h.start()
       threadsList.append(h)
       
    for k in range(0,args.number):
		threadsList[k].join()
    tend = datetime.now()
    tTotal=tend - tstart
    total_seconds=tTotal.total_seconds()
    urlList= d.url.split("/")
    docName=urlList[len(urlList)-1]
    if(docName==''):
		docName='index.html'
    
    f = open("{}".format(docName),'w')
    teststart= datetime.now()
    for j in range(0, args.number):
		f.write(s.dictionary[j]) 
    f.close()
    print('{} {} {} {}'.format(d.url,args.number,d.size,total_seconds))
			
