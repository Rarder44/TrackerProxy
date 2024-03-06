import requests
from urllib.parse import urlparse
def followUntilUDP(url,timeout=1):
    if url.startswith("udp"):
        return True,url
    
    while True:
        try:
            r = requests.get(url,allow_redirects=False,timeout=timeout)
        except:
            return False,None
        
        if r.status_code==302:
            url = r.headers['Location']
            if url.startswith("udp"):
                return True,url
            
        return False,r


def myQueryURLparse(queryStr):
    
    # Parse the query string from the URL
    parsed_url = urlparse('?' + queryStr)

    # Split the query string into a dictionary of query parameters
    query_params = dict(pair.split('=') for pair in parsed_url.query.split('&'))

    return query_params
    
def getServerList(url):
    urls= requests.get(url).text.split('\n')
    urls = [url for url in urls if url != '']
    return urls

def getMyIP():
    return requests.get("https://ifconfig.me").text


