# Technical Documentation - TrackerProxy

**[Italiano](#documentazione-tecnica-italiano) | [English](#technical-documentation-english)**

---

## Technical Documentation English

### 🏗️ Architecture

```
┌──────────────────┐
│  Torrent Client  │
│  (qBittorrent,   │
│   Transmission)  │
└────────┬─────────┘
         │ HTTP Announce Request
         │ info_hash, peer_id, port, etc.
         ▼
┌──────────────────────────────────────┐
│     TrackerProxy (Flask Server)       │
│  ┌────────────────────────────────┐  │
│  │ server.py (HTTP Server)        │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │ TrackerProxy.py (Logic)        │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │ UDPTrackerClient.py (UDP)      │  │
│  └────────────────────────────────┘  │
└────────┬─────────────────────────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │          │          │          │
    ▼          ▼          ▼          ▼
┌─────────┐┌────────┐┌─────────┐┌──────────┐
│ Tracker ││Tracker ││ Tracker ││ Tracker  │
│  HTTP   ││ UDP    ││ HTTP    ││  UDP     │
│   #1    ││  #2    ││  #3     ││  #4      │
└────┬────┘└───┬────┘└────┬────┘└────┬─────┘
     │         │          │         │
     └────┬────┴──────┬───┴────┬────┘
          │           │        │
          ▼           ▼        ▼
    ┌─────────────────────────────────┐
    │ Peer List Aggregation           │
    │ - Combine peer lists            │
    │ - Remove duplicates             │
    │ - Merge statistics              │
    └────────┬────────────────────────┘
             │
             ▼ Bencode Response
    ┌──────────────────────────────┐
    │  Torrent Client              │
    │  (Receives aggregated peers)  │
    └──────────────────────────────┘
```

### 📡 Protocol Flow

#### 1. Client Request to TrackerProxy

```
GET /announce/?info_hash=%XX...&peer_id=-qB5140-...&port=38806&uploaded=0&downloaded=0&left=100000&numwant=200&compact=1
HTTP/1.1

Headers:
    Host: tracker.example.com
    Connection: close
```

Query Parameters:
```
info_hash     : Binary SHA1 hash of .torrent file (URL-encoded)
peer_id       : Unique client identifier (20 bytes)
port          : Port client is listening on
uploaded      : Bytes uploaded so far
downloaded    : Bytes downloaded so far
left          : Bytes remaining to download
numwant       : Number of peers requested (200 typical)
compact       : Return peers in compact format (1 = yes)
no_peer_id    : Don't include peer_id in response (1 = yes)
event         : "started", "completed", "stopped", or omitted
```

#### 2. TrackerProxy Processing

**Step 1: Parse Request**
```python
# Extract parameters from query string
info_hash = URL_decode(info_hash)
peer_id = query["peer_id"]
port = int(query["port"])
# ... etc
```

**Step 2: Load Tracker List**
```python
serverList = [
    "http://tracker1.example.com/announce",
    "udp://tracker2.example.com:6969/announce",
    "http://tracker3.example.com/announce",
    # ... up to 100+ trackers
]
```

**Step 3: Forward to Each Tracker**

For **HTTP Trackers**:
```
GET http://tracker.example.com/announce?info_hash=...&peer_id=...&port=...
```
Response: Bencode dictionary with peers list

For **UDP Trackers**:
```
1. Connect (UDP packet 0)
   - Send: [connection_id=0, action=0, transaction_id]
   - Recv: [action=0, transaction_id, connection_id]

2. Announce (UDP packet 1)
   - Send: [connection_id, action=1, transaction_id, info_hash, peer_id,
            downloaded, left, uploaded, event, ip, key, numwant, port]
   - Recv: [action=1, transaction_id, interval, leechers, seeders, peers]
```

**Step 4: Aggregate Responses**
```python
# Combine responses from all trackers
total_peers = []
for tracker_response in all_responses:
    total_peers.extend(tracker_response.peers)

# Remove duplicates
total_peers = remove_duplicates(total_peers)

# Calculate statistics
result = {
    "complete": max(seeders),
    "incomplete": max(leechers),
    "interval": max(intervals),
    "peers": total_peers
}
```

#### 3. Response to Client

Bencode format:
```python
{
    b'complete': 350,           # Number of complete peers (seeders)
    b'incomplete': 200,         # Number of incomplete peers (leechers)
    b'interval': 1750,          # Recommended interval until next announce
    b'peers': b'\xc0\xa8\x01\x01\x1a\xe1...'  # Compact peer list (6 bytes per peer: 4 bytes IP + 2 bytes port)
}
```

Compact Peer Format (6 bytes per peer):
```
Bytes 1-4: IPv4 address (4 octets)
Bytes 5-6: Port number (big-endian)

Example: c0a80101 1ae1
→ 192.168.1.1 : 6881
  │    │   │  │  │    │
  192  168 1  1  27   225
```

### 🔄 Error Handling

#### Tracker Connection Errors

```
Connection Error
├─ DNS Resolution Failed
│  └─ [Errno -2] Name resolution failed
│     (Tracker hostname doesn't resolve)
│
├─ Connection Refused
│  └─ [Errno 111] Connection refused
│     (Tracker server is down)
│
├─ Timeout
│  └─ asyncio.TimeoutError
│     (Tracker not responding within HTTPtimeout/UDPtimeout)
│
└─ Network Unreachable
   └─ [Errno 113] No route to host
      (Network path not available)
```

#### Tracker Server Errors

```
UDP Error Response (action=3)
├─ "Infohash not found"
├─ "Torrent not allowed"
├─ "Client IP blocked"
└─ Custom error message

HTTP Error Response
├─ 404 Not Found (endpoint doesn't exist)
├─ 403 Forbidden (client blocked)
├─ 500 Server Error (tracker malfunction)
└─ Other HTTP error codes
```

#### TrackerProxy Recovery

```python
# For each tracker
try:
    response = announce_to_tracker(tracker)
except TimeoutError:
    logger.warning(f"Timeout: {tracker}")
    response = None
except ConnectionError:
    logger.warning(f"Connection failed: {tracker}")
    response = None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    response = None

# Continue to next tracker regardless
# Return aggregated results from successful trackers
```

### ⚙️ Configuration Details

#### settings.py

```python
HTTPtimeout = 2        # Seconds to wait for HTTP responses
UDPtimeout = 2         # Seconds to wait for UDP responses

serverListUrl = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"

# List is downloaded once at startup
# File format: one tracker URL per line
# Example content:
# http://tracker1.example.com/announce
# udp://tracker2.example.com:6969/announce
# https://tracker3.example.com:443/announce
```

#### Port Binding

```python
# In server.py
app.run(
    port=1337,              # Port to listen on
    host="0.0.0.0",         # 0.0.0.0 = accept from any interface
    debug=False,            # Disable Flask debug mode (security)
    use_reloader=False      # Disable reloader (better for production)
)
```

### 📊 Performance Characteristics

#### Concurrent Requests

```
Per Request:
- 1 client connection (torrent client) → Flask HTTP server
- 50-150 tracker connections (simultaneous)
  - HTTP connections: blocking with timeout
  - UDP connections: async with timeout
- Response time: max(HTTPtimeout, UDPtimeout) + processing
  
Typical: 2-4 seconds per client request
```

#### Resource Usage

```
Memory:
- Base: ~50 MB (Flask + Python runtime)
- Per idle connection: ~1 KB
- Per active request: ~5-10 MB (temporary)

CPU:
- Idle: <1%
- Per request: 10-20% for 2-4 seconds

Network:
- Bandwidth: Minimal (tracker data << peer data)
- Connections: 50-200 simultaneous possible
```

#### Scaling

```
Single Instance (1 server):
- Supports: 10-100 concurrent torrents
- Supports: 100-1000 announces/minute
- Fits: Raspberry Pi, VPS micro tier

Load Balancing (multiple servers):
- Use round-robin DNS or load balancer
- Share tracker list across instances
- Minimal state needed per instance
```

### 🔐 Security Considerations

#### What TrackerProxy Sees

```
✓ Visible to TrackerProxy:
  - Torrent info_hash
  - Your client port
  - Your peer_id
  - Download progress
  - IP address (implicit in connection)

✗ NOT visible to TrackerProxy:
  - Torrent file content
  - Other peers' data
  - Tracker authentication tokens
```

#### What Trackers See

```
✓ Each tracker sees:
  - Your announce request (usual tracker data)
  - Your IP address (same as without proxy)
  - Your port
  - Download progress

⚠️ Note:
  - Trackers see ONE connection (from proxy server)
  - All client torrents appear to come from proxy IP
  - Tracker cannot identify individual clients
```

#### Recommendations

```
1. Use HTTPS trackers when available
   - Trackers support HTTPS (some do)
   - Encrypts request parameters

2. Configure firewall
   - Restrict port 1337 access to local network
   - Or use firewall rules (iptables, Windows Firewall)

3. Monitor logs
   - Check logs/tracker_proxy_errors.log
   - Look for suspicious connection patterns

4. Update tracker lists regularly
   - Daily recommended
   - Remove dead/spam trackers automatically
```

---

## Documentazione Tecnica Italiano

### 🏗️ Architettura

```
┌──────────────────┐
│  Client Torrent  │
│  (qBittorrent,   │
│   Transmission)  │
└────────┬─────────┘
         │ Richiesta Announce HTTP
         │ info_hash, peer_id, port, etc.
         ▼
┌──────────────────────────────────────┐
│   TrackerProxy (Server Flask)         │
│  ┌────────────────────────────────┐  │
│  │ server.py (Server HTTP)        │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │ TrackerProxy.py (Logica)       │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │ UDPTrackerClient.py (UDP)      │  │
│  └────────────────────────────────┘  │
└────────┬─────────────────────────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │          │          │          │
    ▼          ▼          ▼          ▼
┌─────────┐┌────────┐┌─────────┐┌──────────┐
│ Tracker ││Tracker ││ Tracker ││ Tracker  │
│  HTTP   ││ UDP    ││ HTTP    ││  UDP     │
│   #1    ││  #2    ││  #3     ││  #4      │
└────┬────┘└───┬────┘└────┬────┘└────┬─────┘
     │         │          │         │
     └────┬────┴──────┬───┴────┬────┘
          │           │        │
          ▼           ▼        ▼
    ┌─────────────────────────────────┐
    │ Aggregazione Lista Peer         │
    │ - Combina liste peer            │
    │ - Rimuove duplicati             │
    │ - Unisce statistiche            │
    └────────┬────────────────────────┘
             │
             ▼ Risposta Bencode
    ┌──────────────────────────────┐
    │  Client Torrent              │
    │  (Riceve peer aggregati)     │
    └──────────────────────────────┘
```

### 📡 Flusso Protocollo

#### 1. Richiesta del Client a TrackerProxy

```
GET /announce/?info_hash=%XX...&peer_id=-qB5140-...&port=38806&uploaded=0&downloaded=0&left=100000&numwant=200&compact=1
HTTP/1.1

Headers:
    Host: tracker.example.com
    Connection: close
```

Parametri Query:
```
info_hash     : Hash SHA1 binario del file .torrent (URL-encoded)
peer_id       : Identificatore univoco client (20 byte)
port          : Porta in ascolto del client
uploaded      : Byte caricati finora
downloaded    : Byte scaricati finora
left          : Byte rimanenti da scaricare
numwant       : Numero di peer richiesti (200 tipico)
compact       : Ritorna peer in formato compatto (1 = sì)
no_peer_id    : Non includere peer_id in risposta (1 = sì)
event         : "started", "completed", "stopped", o omesso
```

#### 2. Elaborazione TrackerProxy

**Passo 1: Analizza Richiesta**
```python
# Estrae parametri dalla query string
info_hash = URL_decode(info_hash)
peer_id = query["peer_id"]
port = int(query["port"])
# ... etc
```

**Passo 2: Carica Lista Tracker**
```python
serverList = [
    "http://tracker1.example.com/announce",
    "udp://tracker2.example.com:6969/announce",
    "http://tracker3.example.com/announce",
    # ... fino a 100+ tracker
]
```

**Passo 3: Inoltra a Ogni Tracker**

Per **Tracker HTTP**:
```
GET http://tracker.example.com/announce?info_hash=...&peer_id=...&port=...
```
Risposta: Dizionario Bencode con lista peer

Per **Tracker UDP**:
```
1. Connessione (Pacchetto UDP 0)
   - Invia: [connection_id=0, action=0, transaction_id]
   - Riceve: [action=0, transaction_id, connection_id]

2. Announce (Pacchetto UDP 1)
   - Invia: [connection_id, action=1, transaction_id, info_hash, peer_id,
            downloaded, left, uploaded, event, ip, key, numwant, port]
   - Riceve: [action=1, transaction_id, interval, leechers, seeders, peers]
```

**Passo 4: Aggrega Risposte**
```python
# Combina risposte da tutti i tracker
total_peers = []
for tracker_response in all_responses:
    total_peers.extend(tracker_response.peers)

# Rimuove duplicati
total_peers = remove_duplicates(total_peers)

# Calcola statistiche
result = {
    "complete": max(seeders),
    "incomplete": max(leechers),
    "interval": max(intervals),
    "peers": total_peers
}
```

#### 3. Risposta al Client

Formato Bencode:
```python
{
    b'complete': 350,           # Numero peer completi (seeder)
    b'incomplete': 200,         # Numero peer incompleti (leech)
    b'interval': 1750,          # Intervallo consigliato fino prossimo announce
    b'peers': b'\xc0\xa8\x01\x01\x1a\xe1...'  # Lista peer compatta (6 byte per peer: 4 byte IP + 2 byte porta)
}
```

Formato Peer Compatto (6 byte per peer):
```
Byte 1-4: Indirizzo IPv4 (4 ottetti)
Byte 5-6: Numero porta (big-endian)

Esempio: c0a80101 1ae1
→ 192.168.1.1 : 6881
  │    │   │  │  │    │
  192  168 1  1  27   225
```

### 🔄 Gestione Errori

#### Errori di Connessione Tracker

```
Errore di Connessione
├─ Errore Risoluzione DNS
│  └─ [Errno -2] Name resolution failed
│     (Hostname tracker non risolve)
│
├─ Connessione Rifiutata
│  └─ [Errno 111] Connection refused
│     (Server tracker è giù)
│
├─ Timeout
│  └─ asyncio.TimeoutError
│     (Tracker non risponde entro HTTPtimeout/UDPtimeout)
│
└─ Rete Irraggiungibile
   └─ [Errno 113] No route to host
      (Percorso di rete non disponibile)
```

#### Errori Server Tracker

```
Risposta Errore UDP (action=3)
├─ "Infohash not found"
├─ "Torrent not allowed"
├─ "Client IP blocked"
└─ Messaggio errore personalizzato

Risposta Errore HTTP
├─ 404 Not Found (endpoint non esiste)
├─ 403 Forbidden (client bloccato)
├─ 500 Server Error (malfunzionamento tracker)
└─ Altri codici errore HTTP
```

#### Recupero TrackerProxy

```python
# Per ogni tracker
try:
    response = announce_to_tracker(tracker)
except TimeoutError:
    logger.warning(f"Timeout: {tracker}")
    response = None
except ConnectionError:
    logger.warning(f"Connection failed: {tracker}")
    response = None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    response = None

# Continua al tracker successivo indipendentemente
# Ritorna risultati aggregati da tracker riusciti
```

### ⚙️ Dettagli Configurazione

#### settings.py

```python
HTTPtimeout = 2        # Secondi da aspettare per risposte HTTP
UDPtimeout = 2         # Secondi da aspettare per risposte UDP

serverListUrl = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"

# Lista scaricata una volta all'avvio
# Formato file: un URL tracker per riga
# Contenuto esempio:
# http://tracker1.example.com/announce
# udp://tracker2.example.com:6969/announce
# https://tracker3.example.com:443/announce
```

#### Binding Porta

```python
# In server.py
app.run(
    port=1337,              # Porta in ascolto
    host="0.0.0.0",         # 0.0.0.0 = accetta da qualsiasi interfaccia
    debug=False,            # Disabilita modalità debug Flask (sicurezza)
    use_reloader=False      # Disabilita reloader (migliore per produzione)
)
```

### 📊 Caratteristiche Prestazioni

#### Richieste Concorrenti

```
Per Richiesta:
- 1 connessione client (client torrent) → server HTTP Flask
- 50-150 connessioni tracker (simultanee)
  - Connessioni HTTP: bloccanti con timeout
  - Connessioni UDP: async con timeout
- Tempo risposta: max(HTTPtimeout, UDPtimeout) + elaborazione
  
Tipico: 2-4 secondi per richiesta client
```

#### Utilizzo Risorse

```
Memoria:
- Base: ~50 MB (Flask + Python runtime)
- Per connessione inattiva: ~1 KB
- Per richiesta attiva: ~5-10 MB (temporaneo)

CPU:
- Inattivo: <1%
- Per richiesta: 10-20% per 2-4 secondi

Rete:
- Larghezza banda: Minima (dati tracker << dati peer)
- Connessioni: 50-200 simultanee possibili
```

#### Scalabilità

```
Istanza Singola (1 server):
- Supporta: 10-100 torrent concorrenti
- Supporta: 100-1000 announce/minuto
- Adatto: Raspberry Pi, istanza micro VPS

Bilanciamento Carico (server multipli):
- Usa DNS round-robin o load balancer
- Condividi lista tracker tra istanze
- Stato minimo necessario per istanza
```

### 🔐 Considerazioni Sicurezza

#### Cosa Vede TrackerProxy

```
✓ Visibile a TrackerProxy:
  - Info_hash torrent
  - Porta client
  - Peer_id
  - Progresso download
  - Indirizzo IP (implicito nella connessione)

✗ NON visibile a TrackerProxy:
  - Contenuto file torrent
  - Dati altri peer
  - Token autenticazione tracker
```

#### Cosa Vedono i Tracker

```
✓ Ogni tracker vede:
  - Richiesta announce (dati tracker normali)
  - Indirizzo IP (stesso senza proxy)
  - Porta
  - Progresso download

⚠️ Nota:
  - Tracker vede UNA connessione (da server proxy)
  - Tutti i torrent client sembrano venire da IP proxy
  - Tracker non può identificare singoli client
```

#### Raccomandazioni

```
1. Usa tracker HTTPS quando disponibili
   - Alcuni tracker supportano HTTPS
   - Cripta parametri richiesta

2. Configura firewall
   - Limita accesso porta 1337 a rete locale
   - O usa regole firewall (iptables, Windows Firewall)

3. Monitora log
   - Controlla logs/tracker_proxy_errors.log
   - Cerca pattern connessioni sospette

4. Aggiorna liste tracker regolarmente
   - Consigliato giornaliero
   - Rimuove tracker morti/spam automaticamente
```
