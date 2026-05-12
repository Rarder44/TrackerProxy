# Guida al Logging di TrackerProxy

## Panoramica

Il sistema di logging è stato completamente rivisto per fornire visibilità completa su:
- Dati ricevuti dal client
- Elaborazione di ogni tracker
- Errori specifici e dettagliati
- Risposte finali

Tutti i log sono prefissati con `[TrackerProxy]` per facilità di identificazione.

## Output dei Log

### 1. Console (stdout)
Mostra tutti i log in tempo reale con formato:
```
TIMESTAMP - [TrackerProxy] - LEVEL - MESSAGGIO
```

### 2. File di Log
I log vengono salvati in due file nella directory `logs/`:

**tracker_proxy.log** (10 MB, rotating)
- Contiene tutti i log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Rotazione automatica dopo 10 MB
- Mantiene ultimi 5 backup

**tracker_proxy_errors.log** (5 MB, rotating)
- Solo ERROR e CRITICAL
- Rotazione automatica dopo 5 MB
- Mantiene ultimi 3 backup

## Flusso dei Log per una Richiesta

### Inizio Richiesta
```
[SERVER] ========== NEW ANNOUNCE REQUEST ==========
[SERVER] Raw query string (XXX bytes): [primo 200 char della query]
[SERVER] Client IP: 127.0.0.1
[SERVER] Request path: /announce/
```

### Parsing della Query
```
[announce] Starting announce with N trackers
[announce] Query parameters: info_hash=..., peer_id=..., port=..., uploaded=..., downloaded=..., left=...
```

### Processing di Ogni Tracker
```
[announce] [1/N] Processing tracker: udp://tracker-1.example.com:6969/announce
[announce] [1/N] Tracker is UDP: udp://...
[announce] [1/N] Creating UDP client for: udp://...
[announce] [1/N] Sending UDP announce request to...
[announce] [1/N] ✓ UDP announce successful: seeders=100, leechers=50, peers=200
```

O in caso di errore:
```
[announce] [2/N] Processing tracker: http://tracker-2.example.com/announce
[announce] [2/N] Making HTTP GET request to: http://...
[announce] [2/N] HTTP response status: 200
[announce] [2/N] ✓ HTTP announce successful: seeders=50, leechers=25, peers=100
```

Errori specifici:
```
[announce] [3/N] Processing tracker: udp://tracker-3.example.com:6969/announce
[followUntilUDP] Connection error for URL 'http://...': [Errno -2] Name resolution failed
[announce] [3/N] ✓ [unavailable] Connection failed
```

### Risposta Finale
```
[announce] SUMMARY - Successful: 8/10, Failed: 2/10
[announce] FINAL RESPONSE - Total peers: 1245, seeders=350, leechers=200
[SERVER] Announce completed successfully
[SERVER] Response: 1245 peers, 350 seeders, 200 leechers
[SERVER] Sample peers:
[SERVER]   - 192.168.1.1:6881
[SERVER]   - 10.0.0.1:6882
[SERVER] ========== REQUEST COMPLETED ==========
```

## Livelli di Log

### DEBUG
- Dettagli di parsing
- Connessioni UDP/HTTP in corso
- Risposte parziali

### INFO
- Inizio/fine richieste
- Successo di tracker
- Risposte finali e statistiche

### WARNING
- Tracker falliti
- Timeout
- Risposte vuote

### ERROR
- Errori di parsing
- Errori di connessione
- Eccezioni inaspettate
- Traceback completo

## Casi di Risoluzione dei Problemi

### "Name not resolved" per un tracker
Se vedi:
```
[followUntilUDP] Connection error for URL 'udp://tracker-udp.gbitt.info:80/announce': 
    [Errno -2] Name resolution failed
```

Controlla:
1. Il tracker è online? Prova a pingarlo manualmente
2. La risoluzione DNS della macchina è corretta?
3. È un problema temporaneo di rete?

Il tracker verrà saltato automaticamente e il proxy continuerà con i successivi.

### Caratteri Speciali nei Dati
Tutti i dati URL-encoded vengono loggati come ricevuti:
```
[SERVER] Raw query string (245 bytes): info_hash=%C7r%E7Q...&peer_id=...
[announce] Query parameters: info_hash=..., peer_id=-qB5140-VCE~-7Dov5H9, ...
```

Se vedi errori durante il parsing, cerca nel log ERROR:
```
[announce] Error parsing query string: ValueError: ...
```

### Tracker Costantemente Falliti
Se vedi:
```
[announce] [5/10] ✗ udp://tracker-x.com:6969/announce - No valid response
```

Verificare nei log quale errore specifico si verifica:
- `UDP timeout` - Il tracker è lento, aumenta timeout in settings.py
- `Connection error` - Il tracker potrebbe essere down
- `Server error: ...` - Il tracker ha restituito un errore

## Impostazioni di Debug

### Abilitare/Disabilitare Debug Mode
In `server.py`, cambia il livello:
```python
logger = setup_logging(log_level=logging.DEBUG)  # Molto verboso
logger = setup_logging(log_level=logging.INFO)   # Solo info importanti
logger = setup_logging(log_level=logging.WARNING) # Solo avvertimenti e errori
```

### Modificare Timeout
In `settings.py`:
```python
HTTPtimeout = 2    # Secondi per richieste HTTP
UDPtimeout = 2     # Secondi per richieste UDP
```

Se vedi molti timeout UDP, aumenta il valore.

## Analisi di una Sessione

Per debug completo, guarda il file `logs/tracker_proxy.log`:

```bash
# Mostra solo errori
tail -f logs/tracker_proxy.log | grep ERROR

# Mostra un tracker specifico
tail -f logs/tracker_proxy.log | grep "tracker-name.com"

# Mostra statistiche finali
tail -f logs/tracker_proxy.log | grep "SUMMARY\|FINAL RESPONSE"
```

## Note Importanti

1. **Privacy**: I log contengono info_hash e peer_id. Non condividere i log pubblicamente.
2. **Spazio Disco**: I log vanno in rotating automaticamente. Ogni log può raggiungere 10-15 MB prima di rotare.
3. **Performance**: DEBUG level genera molti log. Per produzione usa INFO o WARNING.
4. **Caratteri Speciali**: Vengono loggati come UTF-8. Se vedi strani caratteri, è OK - potrebbero essere parte del protocollo bittorrent.
