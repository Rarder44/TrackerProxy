import requests
from urllib.parse import urlparse
import logging

logger = logging.getLogger('[TrackerProxy]')

def followUntilUDP(url, timeout=1):
    """
    Segue i redirect fino a trovare un URL UDP o riceve la risposta HTTP.
    Ritorna (is_udp, data) dove data è l'URL UDP o la risposta HTTP.
    """
    logger.debug(f"[followUntilUDP] Starting with URL: {url}")
    
    if url.startswith("udp"):
        logger.debug(f"[followUntilUDP] URL is already UDP: {url}")
        return True, url
    
    while True:
        try:
            logger.debug(f"[followUntilUDP] Making HTTP GET request to: {url}")
            r = requests.get(url, allow_redirects=False, timeout=timeout)
            logger.debug(f"[followUntilUDP] HTTP response status: {r.status_code}")
            
            if r.status_code == 302:
                redirect_url = r.headers['Location']
                logger.info(f"[followUntilUDP] Redirect (302) to: {redirect_url}")
                url = redirect_url
                if url.startswith("udp"):
                    logger.info(f"[followUntilUDP] Redirect leads to UDP: {url}")
                    return True, url
                
            else:
                logger.debug(f"[followUntilUDP] HTTP response received (status {r.status_code}), returning HTTP response")
                return False, r
        
        except requests.exceptions.Timeout as e:
            logger.warning(f"[followUntilUDP] Timeout error for URL '{url}': {e}")
            return False, None
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"[followUntilUDP] Connection error for URL '{url}': {e}")
            return False, None
        except Exception as e:
            logger.error(f"[followUntilUDP] Unexpected error for URL '{url}': {type(e).__name__}: {e}")
            return False, None

def myQueryURLparse(queryStr):
    """Parse query string into dictionary"""
    try:
        # Parse the query string from the URL
        parsed_url = urlparse('?' + queryStr)

        # Split the query string into a dictionary of query parameters
        query_params = dict(pair.split('=', 1) for pair in parsed_url.query.split('&') if '=' in pair)
        
        logger.debug(f"[myQueryURLparse] Parsed {len(query_params)} parameters from query string")
        logger.debug(f"[myQueryURLparse] Parameters: {list(query_params.keys())}")
        
        return query_params
    except Exception as e:
        logger.error(f"[myQueryURLparse] Error parsing query string: {e}")
        raise
    
def getServerList(url):
    """Scarica la lista di tracker dal URL fornito"""
    try:
        logger.info(f"[getServerList] Fetching tracker list from: {url}")
        response = requests.get(url)
        urls = response.text.split('\n')
        urls = [u.strip() for u in urls if u.strip() != '']
        logger.info(f"[getServerList] Loaded {len(urls)} trackers from server list")
        return urls
    except Exception as e:
        logger.error(f"[getServerList] Error fetching server list: {e}")
        return []

def getMyIP():
    """Ottiene l'IP pubblico della macchina"""
    try:
        ip = requests.get("https://ifconfig.me").text
        logger.info(f"[getMyIP] Public IP: {ip}")
        return ip
    except Exception as e:
        logger.error(f"[getMyIP] Error fetching public IP: {e}")
        return "0.0.0.0"

