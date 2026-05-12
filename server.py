#!/usr/bin/python
from flask import Flask
from flask import request
from tool import getMyIP, getServerList
from TrackerProxy import announce
from settings import serverListUrl
from Peer import Peer
from TrackerResponse import TrakerResponse
from logging_config import setup_logging
import logging
import sys

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

serverList = []

# Setup centralized logging
logger = setup_logging(log_level=logging.DEBUG)


@app.route('/announce/')
def announce_proxy():
    """
    Main announce endpoint - receives tracker requests and forwards them to multiple trackers
    """
    logger.info("=" * 80)
    logger.info("[SERVER] ========== NEW ANNOUNCE REQUEST ==========")
    
    # Get raw query string
    query = request.query_string.decode()
    logger.info(f"[SERVER] Raw query string ({len(query)} bytes): {query[:200]}{'...' if len(query) > 200 else ''}")
    
    if query == '':
        logger.warning("[SERVER] Empty query string received")
        return "error", 400
    
    # Log client info
    logger.info(f"[SERVER] Client IP: {request.remote_addr}")
    logger.info(f"[SERVER] Request path: {request.path}")
    
    try:
        logger.info("[SERVER] Starting announce processing...")
        resp = announce(query, serverList)
        
        # Se non abbiamo ottenuto risposta da nessun tracker
        if resp is None:
            logger.warning("[SERVER] No valid response from any tracker - returning empty response")
            empty_response = TrakerResponse()
            return empty_response.bencode()
        
        # Log della risposta
        logger.info(f"[SERVER] Announce completed successfully")
        logger.info(f"[SERVER] Response: {len(resp.peers)} peers, {resp.complete} seeders, {resp.incomplete} leechers")
        
        # Log dei peer principali (max 5)
        if resp.peers:
            logger.debug(f"[SERVER] Sample peers:")
            for peer in resp.peers[:5]:
                logger.debug(f"[SERVER]   - {peer.ip}:{peer.port}")
        
        logger.info("[SERVER] ========== REQUEST COMPLETED ==========")
        logger.info("=" * 80)
        
        return resp.bencode()
    
    except Exception as e:
        logger.error(f"[SERVER] Error in announce_proxy: {type(e).__name__}: {e}", exc_info=True)
        logger.warning("[SERVER] Returning empty response due to error")
        logger.info("[SERVER] ========== REQUEST FAILED ==========")
        logger.info("=" * 80)
        
        # Ritorna una risposta valida anche in caso di errore
        empty_response = TrakerResponse()
        return empty_response.bencode()


@app.route("/<name>")
def test(name):
    logger.info(f"[SERVER] Test route called with: {name}")
    return "this is a test code=====" + name


@app.route("/ip")
def ip():
    logger.info("[SERVER] IP route called")
    return getMyIP()


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("[SERVER] ========== STARTING TRACKER PROXY ==========")
    
    logger.info(f"[SERVER] Loading tracker list from: {serverListUrl}")
    serverList = getServerList(serverListUrl)
    logger.info(f"[SERVER] Loaded {len(serverList)} trackers")
    
    # Log first 5 trackers
    logger.debug("[SERVER] First 5 trackers:")
    for tracker in serverList[:5]:
        logger.debug(f"[SERVER]   - {tracker}")
    
    logger.info("[SERVER] Starting Flask server on 0.0.0.0:1337")
    logger.info("=" * 80)
    
    app.run(port=1337, host="0.0.0.0", debug=False, use_reloader=False)

