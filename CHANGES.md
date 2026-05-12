# Miglioramenti al Logging - Riepilogo delle Modifiche

## File Modificati

### 1. **server.py**
- ✅ Aggiunto logging centralizzato con `logging_config.py`
- ✅ Log dettagliato di ogni richiesta in arrivo
- ✅ Log dei dati grezzi (query string, client IP, percorso)
- ✅ Log della risposta finale e statistiche peer
- ✅ Error handling completo con stack trace
- ✅ Separatori visivi per leggibilità
- ✅ Prefisso `[SERVER]` per i log server-level
- ✅ Prefisso `[TrackerProxy]` per i log di processing

### 2. **TrackerProxy.py**
- ✅ Logging completo del flusso di announce
- ✅ Log di parsing query string con parametri importanti
- ✅ Log per ogni tracker processato (numero tracker / totale)
- ✅ Log di successo/fallimento con statistiche
- ✅ Distinzione tra UDP e HTTP tracker
- ✅ Log di errori specifici (timeout, server error, ecc.)
- ✅ Statistiche finali (successi/fallimenti)
- ✅ Conteggio peer aggiunti in merge
- ✅ Tutti i log con prefisso `[announce]` o `[TrackerProxy]`

### 3. **tool.py**
- ✅ Aggiunto logging a `followUntilUDP()` con dettagli delle richieste HTTP
- ✅ Log dei redirect (302) e tracciamento URL
- ✅ Log degli errori specifici: Timeout, ConnectionError, altri errori
- ✅ Logging in `myQueryURLparse()` con conteggio parametri
- ✅ Logging in `getServerList()` con numero tracker caricati
- ✅ Logging in `getMyIP()` con IP pubblico ottenuto
- ✅ Rimosso generico `except: pass` - ora con logging specifico
- ✅ Tutti i log con prefisso `[TrackerProxy]`

### 4. **UDPTrackerClient.py**
- ✅ Aggiornato logger per usare `[TrackerProxy]` come prefisso consistente

### 5. **logging_config.py** (NUOVO)
- ✅ Configurazione centralizzata del logging
- ✅ Output su console con formatter dettagliato
- ✅ Output su file `logs/tracker_proxy.log` (rotating, 10 MB)
- ✅ Output su file `logs/tracker_proxy_errors.log` (rotating, 5 MB, solo errori)
- ✅ Backup automatici (5 backup per main, 3 per errors)
- ✅ Funzione `setup_logging()` per setup facile
- ✅ Funzione `quick_setup()` per debug mode

### 6. **LOGGING_GUIDE.md** (NUOVO)
- ✅ Documentazione completa del sistema di logging
- ✅ Guida al flusso dei log per una richiesta
- ✅ Esempi di output per vari scenari
- ✅ Descrizione dei livelli di log
- ✅ Casi di risoluzione dei problemi
- ✅ Impostazioni di debug

### 7. **test_logging.py** (NUOVO)
- ✅ Script di test per verificare il sistema di logging

## Cosa puoi Verificare Adesso

### Problema Originale: "Name not resolved"
Con il nuovo logging vedrai:
```
[followUntilUDP] Connection error for URL 'udp://tracker-udp.gbitt.info:80/announce': 
    [Errno -2] Name resolution failed
[announce] [3/10] ✗ udp://tracker-udp.gbitt.info:80/announce - No valid response
```

Questo ti dice esattamente quale tracker ha problemi DNS.

### Caratteri Speciali nei Dati
Ora vedi esattamente come vengono passati:
```
[SERVER] Raw query string (245 bytes): info_hash=%C7r%E7Q...
[announce] Query parameters: info_hash=b'...', peer_id='-qB5140-VCE~-7Dov5H9', ...
```

Se c'è un problema di parsing, il log mostrerà esattamente dove:
```
[announce] Error parsing query string: ValueError: invalid literal for int(): '...'
```

## Come Usare

### 1. Eseguire il server
```bash
python server.py
```

I log appariranno su console e verranno salvati in `logs/`.

### 2. Monitorare i log in tempo reale
```bash
# Console mostra tutto
# In background, monitor il file:
tail -f logs/tracker_proxy.log
```

### 3. Cercare errori specifici
```bash
# Solo errori
grep ERROR logs/tracker_proxy.log

# Errori da un tracker specifico
grep "tracker-name.com" logs/tracker_proxy.log

# Statistiche finali
grep "SUMMARY\|FINAL RESPONSE" logs/tracker_proxy.log
```

### 4. Debug di problemi
Controlla `logs/tracker_proxy_errors.log` per i problemi gravi.

## Miglioramenti Chiave

1. **Tracciabilità Completa**: Puoi seguire ogni richiesta dal client all'ultima risposta
2. **Prefissi Consistenti**: `[TrackerProxy]` in tutti i moduli
3. **Informazioni Strutturate**: Ogni log contiene il tipo di operazione e i dettagli rilevanti
4. **Errori Specifici**: Invece di "error!", vedrai esattamente cosa è andato male
5. **File di Log Persistenti**: I log vengono salvati per analisi offline
6. **Rotazione Automatica**: I file non crescono indefinitamente
7. **Visibilità sui Dati**: Vedi i dati grezzi ricevuti dal client

## Note Importanti

- I log contengono informazioni sensibili (info_hash, peer_id). Non condividere pubblicamente.
- La directory `logs/` viene creata automaticamente al primo run.
- Il livello di DEBUG è verbose. Per produzione usa INFO.
- I timeout per HTTP e UDP possono essere modificati in `settings.py` se vedi molti timeout.
