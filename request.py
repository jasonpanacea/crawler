import requests
from bs4 import BeautifulSoup
import os
from gevent import monkey; monkey.patch_socket()
import gevent
import multiprocessing
proxies = {
  "http": "http://127.0.0.1:1080",
  "https": "http://127.0.0.1:1080",
}

def getURLList():
    sid = 2000
    headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer':'http://www.rosmm.com/rosimm/'}
    URLList = []

    while sid > 1800:
        r=requests.get("http://www.rosmm.com/public/ajax.php?action=list&sid="+str(sid)+"&classid=rosimm",  headers=headers)
        r.encoding = 'gb2312'
        # print r.status_code
        html = r.text
        parsed_html = BeautifulSoup(html, "html.parser")
        urls = parsed_html.find_all('li')
        for url in urls:
            URLList.append('http://www.rosmm.com'+url.a.get('href'))
        sid = int(URLList[-1].split('/')[-1].split('.')[0])

    return URLList

def downLoadSerie(serieURL):
    url = serieURL
    print url
    r = requests.get(url)
    print r.status_code
    parsed_html = BeautifulSoup(r.text, "html.parser")
    imgTag = parsed_html.find(id="imgString")
    print imgTag.img.get('src')
    downLink = imgTag.img.get('src')
    imgNo = int(downLink.split('/')[-1].split('-')[-1].split('.')[0])
    prefilename = ('-').join(downLink.split('/')[-1].split('.')[0].split('-')[0:-1])
    print imgNo
    print prefilename

    while True:
        downLink = ('/').join(downLink.split('/')[0:-1]) +'/'+ prefilename + '-' + str(imgNo) + '.jpg'
        r = requests.get(downLink, stream=True)
        if r.status_code == 200:
            imgNo += 1
            filename = downLink.split('/')[-1]
            dirname = filename.split('-')[1]
            print 'Downloading ' + downLink
            if dirname not in os.listdir('./'):
                os.mkdir(dirname)
            with open('./'+dirname+'/'+filename, 'wb') as fd:
                for chunk in r.iter_content(1024):
                    fd.write(chunk)
        else:
            return

def downURLS(URLs):
    for url in URLs:
        downLoadSerie(url)

def write2file(URLs):
    with open("URLs.txt","w+") as f:
        for url in URLs:
            f.write("%s\n" % url)
        f.close()

if __name__ == '__main__':
    print 'getURLList...'
    URLList = getURLList()
    n = len(URLList)
    # write2file(URLList)
    print n
    print 'Start download...'
    # URLList = URLList[::-1]
    # downURLS(URLList[90:])
    # gevent.URLList[85:]joinall([gevent.spawn(downURLS, URLList[0:100]), gevent.spawn(downURLS, URLList[100:200]), gevent.spawn(downURLS, URLList[200:300]), gevent.spawn(downURLS, URLList[300:400])])
    process0 = multiprocessing.Process(target=downURLS,args=(URLList[0:50], ))
    process0.start()
    process1 = multiprocessing.Process(target=downURLS,args=(URLList[50:], ))
    process1.start()
    process0.join()
    process1.join()
    print 'End download'
