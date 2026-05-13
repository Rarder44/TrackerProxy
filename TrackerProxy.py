from TrackerResponse import TrakerResponse
from UDPTrackerClient import TrackerClient, ServerError
from tool import followUntilUDP, myQueryURLparse
from urllib.parse import unquote_to_bytes
import asyncio
from settings import HTTPtimeout
import logging

logger = logging.getLogger('[TrackerProxy]')

def announce(queryURLencoded, serverList):
    """
    Invia richieste di announce a multiple tracker e raccoglie le risposte.
    
    Args:
        queryURLencoded: Query string URL-encoded dalla richiesta client
        serverList: Lista di URL tracker
        
    Returns:
        TrakerResponse: Risposta aggregata da tutti i tracker disponibili
    """
    
    logger.info(f"[announce] Starting announce with {len(serverList)} trackers")
    logger.debug(f"[announce] Raw query: {queryURLencoded[:100]}...")  # Primi 100 char
    
    # Parse della query string
    try:
        res = myQueryURLparse(queryURLencoded)
    except Exception as e:
        logger.error(f"[announce] Failed to parse query string: {e}")
        return None
    
    # Log dei parametri più importanti
    logger.info(f"[announce] Query parameters: "
                f"info_hash={res.get('info_hash', 'MISSING')[:20]}..., "
                f"peer_id={res.get('peer_id', 'MISSING')}, "
                f"port={res.get('port', 'MISSING')}, "
                f"uploaded={res.get('uploaded', 'MISSING')}, "
                f"downloaded={res.get('downloaded', 'MISSING')}, "
                f"left={res.get('left', 'MISSING')}")
    
    finalResponse: TrakerResponse = None
    successful_trackers = 0
    failed_trackers = 0
    
    for idx, server in enumerate(serverList, 1):
        tr = None
        urlq = f"{server}?{queryURLencoded}"
        
        logger.info(f"[announce] [{idx}/{len(serverList)}] Processing tracker: {server}")

        try:
            # Tenta di raggiungere il tracker (HTTP redirect o UDP diretto)
            isUDP, data = followUntilUDP(urlq, HTTPtimeout)
            
            if isUDP:
                logger.debug(f"[announce] [{idx}] Tracker is UDP: {data}")
                
                # Converti la richiesta URL-encoded in richiesta UDP
                try:
                    res_parsed = myQueryURLparse(queryURLencoded)
                    res_parsed["info_hash"] = unquote_to_bytes(res_parsed["info_hash"])
                    peerid = res_parsed["peer_id"].encode()
                    
                    # Event mapping
                    eventMap = {"none": 0, "completed": 1, "started": 2, "stopped": 3}
                    try:
                        eventid = eventMap[res_parsed.get("event", "none")]
                    except:
                        eventid = 0
                    
                    logger.debug(f"[announce] [{idx}] Creating UDP client for: {server}")
                    client = TrackerClient(announce_uri=server, peerid=peerid, max_retransmissions=1)
                    
                    # Effettua announce UDP
                    logger.debug(f"[announce] [{idx}] Sending UDP announce request to {server}")
                    try:
                        tr = asyncio.run(client.announce(
                            res_parsed["info_hash"],
                            int(res_parsed.get("downloaded", 0)),
                            int(res_parsed.get("left", 0)),
                            int(res_parsed.get("uploaded", 0)),
                            eventid,
                            int(res_parsed.get("numwant", 200)),
                            port=int(res_parsed.get("port", 0))
                        ))
                        
                        if tr:
                            logger.info(f"[announce] [{idx}] [OK] UDP announce successful: "
                                      f"seeders={tr.complete}, leechers={tr.incomplete}, peers={len(tr.peers)}")
                        else:
                            logger.warning(f"[announce] [{idx}] UDP announce returned no response")
                    
                    except asyncio.TimeoutError:
                        logger.warning(f"[announce] [{idx}] UDP timeout for {server}")
                        tr = None
                    except ServerError as e:
                        logger.warning(f"[announce] [{idx}] UDP server error for {server}: {e}")
                        tr = None
                    except Exception as e:
                        logger.error(f"[announce] [{idx}] Unexpected error during UDP announce: {type(e).__name__}: {e}")
                        tr = None
                
                except Exception as e:
                    logger.error(f"[announce] [{idx}] Error preparing UDP request: {type(e).__name__}: {e}")
                    tr = None

            else:
                # HTTP response
                if data is not None:
                    try:
                        logger.debug(f"[announce] [{idx}] Received HTTP response, parsing...")
                        d = data._content
                        tr = TrakerResponse.parse(d)
                        
                        if tr:
                            logger.info(f"[announce] [{idx}] [OK] HTTP announce successful: "
                                      f"seeders={tr.complete}, leechers={tr.incomplete}, peers={len(tr.peers)}")
                        else:
                            logger.warning(f"[announce] [{idx}] HTTP response parsing returned None")
                    except Exception as e:
                        logger.error(f"[announce] [{idx}] Error parsing HTTP response: {type(e).__name__}: {e}")
                        tr = None
                else:
                    logger.warning(f"[announce] [{idx}] No HTTP data received from {server}")

        except Exception as e:
            logger.error(f"[announce] [{idx}] Unexpected error processing tracker {server}: {type(e).__name__}: {e}", exc_info=True)
            tr = None

        # Processa il risultato
        if tr is None:
            logger.error(f"[announce] [{idx}] [FAILED] {server} - No valid response")
            failed_trackers += 1
            continue
        
        successful_trackers += 1
        
        # Merge con la risposta finale
        if finalResponse is None:
            finalResponse = tr
            logger.info(f"[announce] [{idx}] Created initial response with {len(tr.peers)} peers")
        else:
            old_peer_count = len(finalResponse.peers)
            finalResponse.merge(tr)
            new_peers = len(finalResponse.peers) - old_peer_count
            logger.info(f"[announce] [{idx}] Merged response, added {new_peers} new peers (total: {len(finalResponse.peers)})")

    # Summary finale
    logger.info(f"[announce] SUMMARY - Successful: {successful_trackers}/{len(serverList)}, Failed: {failed_trackers}/{len(serverList)}")
    if finalResponse:
        logger.info(f"[announce] FINAL RESPONSE - Total peers: {len(finalResponse.peers)}, seeders={finalResponse.complete}, leechers={finalResponse.incomplete}")
    else:
        logger.warning(f"[announce] No valid response from any tracker!")
    
    return finalResponse