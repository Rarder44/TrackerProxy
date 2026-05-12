# TrackerProxy

A torrent tracker proxy that aggregates requests across multiple trackers, providing a single HTTP endpoint for torrent clients.

---

**[Italiano](#italiano) | [English](#english)**

---

## English

### 📋 Overview

**TrackerProxy** is a torrent tracker proxy that acts as an intermediary between your torrent client and multiple tracker servers. Instead of configuring your torrent client with a single tracker URL, you configure it to use TrackerProxy, which then forwards announce requests to a pool of pre-configured trackers and aggregates the responses.

**Key Benefits:**
- **Single Endpoint**: Configure one tracker URL in your torrent client
- **Automatic Updates**: Tracker list updates automatically from remote sources
- **Redundancy**: If one tracker fails, others provide peers
- **HTTP Interface**: Supports torrent clients that use HTTP trackers
- **UDP Support**: Automatically handles UDP trackers through conversion
- **Performance**: Aggregates peer lists from multiple trackers for better swarm participation
- **Visibility**: Comprehensive logging to debug tracker issues

### 🎯 How It Works

```
Torrent Client → TrackerProxy HTTP Server → Multiple Trackers (UDP/HTTP)
                                          ↓
                          Aggregated Peer List → Torrent Client
```

1. **Request**: Torrent client sends an announce request to `http://your-server:1337/announce/`
2. **Forward**: TrackerProxy parses the request and forwards it to multiple trackers
3. **Process**: 
   - For HTTP trackers: Makes direct HTTP requests
   - For UDP trackers: Converts HTTP parameters to UDP protocol
4. **Aggregate**: Collects responses from all trackers
5. **Response**: Combines peer lists and returns to torrent client

### 🚀 Quick Start

#### Prerequisites
- Python 3.8+
- `pip` package manager

#### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/TrackerProxy.git
cd TrackerProxy

# Install dependencies
pip install -r requirements.txt
```

#### Configuration

Edit `settings.py`:

```python
# Timeout for HTTP requests (seconds)
HTTPtimeout = 2

# Timeout for UDP requests (seconds)
UDPtimeout = 2

# URL to fetch tracker list (updates automatically on startup)
serverListUrl = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"

# Alternative: Use all trackers (more but slower)
# serverListUrl = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt"
```

#### Running the Server

```bash
# Windows
python server.py

# Linux/macOS
python3 server.py
```

The server will start on `http://0.0.0.0:1337`

Output:
```
2026-05-12 23:41:00,123 - [TrackerProxy] - INFO - [SERVER] ========== STARTING TRACKER PROXY ==========
2026-05-12 23:41:01,456 - [TrackerProxy] - INFO - [SERVER] Loaded 120 trackers
2026-05-12 23:41:01,789 - [TrackerProxy] - INFO - [SERVER] Starting Flask server on 0.0.0.0:1337
```

### ⚙️ Configuration in Your Torrent Client

Once TrackerProxy is running on your server, configure your torrent client:

#### qBittorrent

1. **Global Tracker**:
   - Go to: `Tools` → `Options` → `BitTorrent`
   - Find: `Additional trackers`
   - Add tracker URL: `http://your-server-ip:1337/announce/`
   - Click: `Apply` → `OK`

2. **Per-Torrent** (Alternative):
   - Right-click torrent → `Properties`
   - Go to: `Trackers` tab
   - Click: `Add tracker`
   - Enter: `http://your-server-ip:1337/announce/`

#### Transmission

1. **Edit torrent**:
   - Right-click torrent → `Properties`
   - Go to: `Trackers` tab
   - Click: `Add`
   - Enter: `http://your-server-ip:1337/announce/`

#### Deluge

1. **Plugin method** (Recommended):
   - Install: `LabelPlus` or tracker management plugin
   - Configure: Add `http://your-server-ip:1337/announce/`

2. **Manual method**:
   - Edit torrent file before adding

#### Aria2

1. **Edit config** (`~/.aria2/aria2.conf`):
   ```
   bt-tracker=http://your-server-ip:1337/announce/
   ```

2. **Or command line**:
   ```bash
   aria2c --bt-tracker="http://your-server-ip:1337/announce/" torrent-file.torrent
   ```

### 📊 Server Address Examples

- **Local Network**: `http://192.168.1.100:1337/announce/`
- **VPS/Server**: `http://your-domain.com:1337/announce/`
- **Docker**: `http://docker-container-ip:1337/announce/`
- **Localhost**: `http://127.0.0.1:1337/announce/` (only on same machine)

### 📝 Tracker Sources

TrackerProxy can use different tracker lists:

```python
# Best working trackers (recommended)
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"

# All trackers (more comprehensive, slower)
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt"

# HTTP trackers only
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_http.txt"

# HTTPS trackers only
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_https.txt"

# Static list (edit settings.py and restart server)
# (manually add tracker URLs to serverList in TrackerProxy.py or settings.py)
```

### 🔍 Monitoring & Troubleshooting

#### View Logs

Real-time console output:
```
python server.py
```

Persistent logs:
```bash
# View all logs
tail -f logs/tracker_proxy.log

# View errors only
tail -f logs/tracker_proxy_errors.log

# Search for specific tracker
grep "tracker-name.com" logs/tracker_proxy.log
```

#### Common Issues

**Issue: No peers returned**
```
Solution: Check that at least one tracker is responsive
          tail -f logs/tracker_proxy.log | grep "SUMMARY"
          Increase UDPtimeout in settings.py if trackers are slow
```

**Issue: "Name resolution failed"**
```
Solution: Check network/DNS connectivity
          Verify tracker URL is correct
          May be temporary - tracker auto-recovers on next request
```

**Issue: Server won't start**
```
Solution: Check port 1337 is not in use
          Run: netstat -an | grep 1337
          Change port in server.py if needed
```

### 📊 Performance Tips

1. **Adjust Timeouts** (settings.py):
   - Slower network: Increase from 2 to 5 seconds
   - Fast network: Can decrease to 1 second

2. **Tracker Selection**:
   - Use `trackers_best.txt` for faster responses
   - Use `trackers_all.txt` for more peers (but slower)

3. **Server Resources**:
   - Light load: Runs on Raspberry Pi, VPS micro instance
   - Each request queries 50-150 trackers concurrently

### 🛠️ Advanced Configuration

#### Custom Tracker List

Edit `settings.py`:
```python
# Static tracker list
serverListUrl = None  # Disable remote list

# Then in server.py, modify:
serverList = [
    "udp://tracker1.com:6969/announce",
    "http://tracker2.com/announce",
    "udp://tracker3.com:80/announce",
]
```

#### Change Port

Edit `server.py` (last line):
```python
app.run(port=8080, host="0.0.0.0", debug=False, use_reloader=False)
```

Then use: `http://your-server:8080/announce/`

#### Docker Support

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 1337

CMD ["python", "server.py"]
```

Build and run:
```bash
docker build -t trackerproxy .
docker run -p 1337:1337 trackerproxy
```

### 📚 Project Structure

```
TrackerProxy/
├── server.py              # Main Flask HTTP server
├── TrackerProxy.py        # Announce request logic
├── UDPTrackerClient.py    # UDP tracker communication
├── TrackerResponse.py     # Peer list parsing
├── tool.py                # Helper functions
├── Peer.py                # Peer data model
├── settings.py            # Configuration
├── logging_config.py      # Logging setup
├── requirements.txt       # Python dependencies
├── LICENSE               # License file
└── README.md             # This file
```

### 📜 License

See LICENSE file for details.

### 🤝 Contributing

Contributions welcome! Please submit pull requests or issues.

---

## Italiano

### 📋 Panoramica

**TrackerProxy** è un proxy per tracker torrent che funge da intermediario tra il tuo client torrent e più server tracker. Invece di configurare il tuo client torrent con un singolo URL tracker, lo configuri per usare TrackerProxy, che poi inoltra le richieste di announce a un pool di tracker pre-configurati e aggrega le risposte.

**Vantaggi Principali:**
- **Singolo Endpoint**: Configura un solo URL tracker nel tuo client torrent
- **Aggiornamenti Automatici**: La lista tracker si aggiorna automaticamente da fonti remote
- **Ridondanza**: Se un tracker fallisce, gli altri forniscono peer
- **Interfaccia HTTP**: Supporta client torrent che usano tracker HTTP
- **Supporto UDP**: Gestisce automaticamente tracker UDP attraverso conversione
- **Prestazioni**: Aggrega liste peer da più tracker per una migliore partecipazione allo sciame
- **Visibilità**: Logging completo per debuggare problemi di tracker

### 🎯 Come Funziona

```
Client Torrent → Server HTTP TrackerProxy → Multiple Tracker (UDP/HTTP)
                                           ↓
                          Lista Peer Aggregata → Client Torrent
```

1. **Richiesta**: Il client torrent invia una richiesta di announce a `http://tuo-server:1337/announce/`
2. **Inoltro**: TrackerProxy analizza la richiesta e la inoltra a più tracker
3. **Elaborazione**:
   - Per tracker HTTP: Effettua richieste HTTP dirette
   - Per tracker UDP: Converte i parametri HTTP in protocollo UDP
4. **Aggregazione**: Raccoglie risposte da tutti i tracker
5. **Risposta**: Combina le liste peer e ritorna al client torrent

### 🚀 Avvio Rapido

#### Prerequisiti
- Python 3.8+
- `pip` package manager

#### Installazione

```bash
# Clona il repository
git clone https://github.com/tuonome/TrackerProxy.git
cd TrackerProxy

# Installa le dipendenze
pip install -r requirements.txt
```

#### Configurazione

Modifica `settings.py`:

```python
# Timeout per richieste HTTP (secondi)
HTTPtimeout = 2

# Timeout per richieste UDP (secondi)
UDPtimeout = 2

# URL da cui scaricare la lista tracker (si aggiorna automaticamente all'avvio)
serverListUrl = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"

# Alternativa: Usa tutti i tracker (più completo ma più lento)
# serverListUrl = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt"
```

#### Esecuzione del Server

```bash
# Windows
python server.py

# Linux/macOS
python3 server.py
```

Il server si avvierà su `http://0.0.0.0:1337`

Output:
```
2026-05-12 23:41:00,123 - [TrackerProxy] - INFO - [SERVER] ========== STARTING TRACKER PROXY ==========
2026-05-12 23:41:01,456 - [TrackerProxy] - INFO - [SERVER] Loaded 120 trackers
2026-05-12 23:41:01,789 - [TrackerProxy] - INFO - [SERVER] Starting Flask server on 0.0.0.0:1337
```

### ⚙️ Configurazione nel Tuo Client Torrent

Una volta che TrackerProxy è in esecuzione sul tuo server, configura il tuo client torrent:

#### qBittorrent

1. **Tracker Globale**:
   - Vai a: `Strumenti` → `Opzioni` → `BitTorrent`
   - Trova: `Tracker addizionali`
   - Aggiungi URL tracker: `http://ip-tuo-server:1337/announce/`
   - Clicca: `Applica` → `OK`

2. **Per Singolo Torrent** (Alternativa):
   - Clicca destro sul torrent → `Proprietà`
   - Vai a: Scheda `Tracker`
   - Clicca: `Aggiungi tracker`
   - Inserisci: `http://ip-tuo-server:1337/announce/`

#### Transmission

1. **Modifica torrent**:
   - Clicca destro sul torrent → `Proprietà`
   - Vai a: Scheda `Tracker`
   - Clicca: `Aggiungi`
   - Inserisci: `http://ip-tuo-server:1337/announce/`

#### Deluge

1. **Metodo plugin** (Consigliato):
   - Installa plugin: `LabelPlus` o di gestione tracker
   - Configura: Aggiungi `http://ip-tuo-server:1337/announce/`

2. **Metodo manuale**:
   - Modifica file torrent prima di aggiungerlo

#### Aria2

1. **Modifica config** (`~/.aria2/aria2.conf`):
   ```
   bt-tracker=http://ip-tuo-server:1337/announce/
   ```

2. **O da riga di comando**:
   ```bash
   aria2c --bt-tracker="http://ip-tuo-server:1337/announce/" file-torrent.torrent
   ```

### 📊 Esempi di Indirizzi Server

- **Rete Locale**: `http://192.168.1.100:1337/announce/`
- **VPS/Server**: `http://tuo-dominio.com:1337/announce/`
- **Docker**: `http://ip-contenitore-docker:1337/announce/`
- **Localhost**: `http://127.0.0.1:1337/announce/` (solo sulla stessa macchina)

### 📝 Fonti Tracker

TrackerProxy può usare diverse liste di tracker:

```python
# Tracker migliori e più affidabili (consigliato)
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"

# Tutti i tracker (più completo, più lento)
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt"

# Solo tracker HTTP
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_http.txt"

# Solo tracker HTTPS
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_https.txt"

# Lista statica (modifica settings.py e riavvia il server)
# (aggiungi manualmente gli URL tracker)
```

### 🔍 Monitoraggio e Risoluzione Problemi

#### Visualizza Log

Output console in tempo reale:
```
python server.py
```

Log persistenti:
```bash
# Visualizza tutti i log
tail -f logs/tracker_proxy.log

# Visualizza solo errori
tail -f logs/tracker_proxy_errors.log

# Cerca un tracker specifico
grep "nome-tracker.com" logs/tracker_proxy.log
```

#### Problemi Comuni

**Problema: Nessun peer ritornato**
```
Soluzione: Verifica che almeno un tracker sia raggiungibile
           tail -f logs/tracker_proxy.log | grep "SUMMARY"
           Aumenta UDPtimeout in settings.py se i tracker sono lenti
```

**Problema: "Name resolution failed"**
```
Soluzione: Verifica la connettività di rete/DNS
           Verifica che l'URL del tracker sia corretto
           Potrebbe essere temporaneo - il tracker si recupera dalla richiesta successiva
```

**Problema: Il server non si avvia**
```
Soluzione: Verifica che la porta 1337 non sia in uso
           Esegui: netstat -an | grep 1337
           Cambia la porta in server.py se necessario
```

### 📊 Suggerimenti per le Prestazioni

1. **Regola i Timeout** (settings.py):
   - Rete lenta: Aumenta da 2 a 5 secondi
   - Rete veloce: Può diminuire a 1 secondo

2. **Selezione Tracker**:
   - Usa `trackers_best.txt` per risposte più veloci
   - Usa `trackers_all.txt` per più peer (ma più lento)

3. **Risorse del Server**:
   - Carico leggero: Funziona su Raspberry Pi, istanza micro VPS
   - Ogni richiesta interroga 50-150 tracker concorrentemente

### 🛠️ Configurazione Avanzata

#### Lista Tracker Personalizzata

Modifica `settings.py`:
```python
# Lista tracker statica
serverListUrl = None  # Disabilita lista remota

# Poi in server.py, modifica:
serverList = [
    "udp://tracker1.com:6969/announce",
    "http://tracker2.com/announce",
    "udp://tracker3.com:80/announce",
]
```

#### Cambia Porta

Modifica `server.py` (ultima riga):
```python
app.run(port=8080, host="0.0.0.0", debug=False, use_reloader=False)
```

Quindi usa: `http://tuo-server:8080/announce/`

#### Supporto Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 1337

CMD ["python", "server.py"]
```

Compila ed esegui:
```bash
docker build -t trackerproxy .
docker run -p 1337:1337 trackerproxy
```

### 📚 Struttura del Progetto

```
TrackerProxy/
├── server.py              # Server HTTP Flask principale
├── TrackerProxy.py        # Logica richiesta announce
├── UDPTrackerClient.py    # Comunicazione tracker UDP
├── TrackerResponse.py     # Parsing lista peer
├── tool.py                # Funzioni di supporto
├── Peer.py                # Modello dati Peer
├── settings.py            # Configurazione
├── logging_config.py      # Configurazione logging
├── requirements.txt       # Dipendenze Python
├── LICENSE               # File licenza
└── README.md             # Questo file
```

### 📜 Licenza

Vedi il file LICENSE per i dettagli.

### 🤝 Contribuire

I contributi sono benvenuti! Per favore invia pull request o issues.
