# Quick Start Guide - TrackerProxy

**[Italiano](#quick-start-italiano) | [English](#quick-start-english)**

---

## Quick Start English

### ⚡ 5-Minute Setup

#### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Run the Server
```bash
python server.py
```

You should see:
```
[SERVER] Loaded 120 trackers
[SERVER] Starting Flask server on 0.0.0.0:1337
```

#### 3. Configure Your Torrent Client

**qBittorrent Example:**
1. Tools → Options → BitTorrent
2. Find "Additional trackers"
3. Add: `http://YOUR_SERVER_IP:1337/announce/`
4. Click Apply

**That's it!** Your torrent client now uses TrackerProxy.

---

### 🖥️ Finding Your Server IP

- **Same Computer**: `http://127.0.0.1:1337/announce/`
- **Network Computer**: `http://192.168.X.X:1337/announce/`
  - Find it: Run `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
- **VPS/Cloud Server**: `http://your-domain.com:1337/announce/`

---

### ⚙️ Basic Troubleshooting

**Problem: Server won't start**
```
→ Check if port 1337 is already in use
→ Run: netstat -an | grep 1337
→ Or change port in server.py (last line)
```

**Problem: Torrent client can't find tracker**
```
→ Check firewall (port 1337 must be open)
→ Verify IP address is correct
→ Try: curl http://127.0.0.1:1337/announce/
```

**Problem: No peers showing up**
```
→ Check logs: tail -f logs/tracker_proxy.log
→ Look for: "SUMMARY" line
→ If all trackers fail: increase UDPtimeout in settings.py
```

---

### 📋 Settings

Edit `settings.py` to customize:

```python
HTTPtimeout = 2      # Seconds to wait for HTTP trackers
UDPtimeout = 2       # Seconds to wait for UDP trackers
serverListUrl = "..."  # Which tracker list to use
```

#### Popular Tracker Lists
```python
# Best & fastest (recommended)
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"

# More trackers, might be slower
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt"
```

---

### 📝 Popular Torrent Client Configuration

| Client | Steps |
|--------|-------|
| **qBittorrent** | Tools → Options → BitTorrent → Additional trackers |
| **Transmission** | Edit → Preferences → Remote → Tracker |
| **Deluge** | Preferences → Network → Tracker → Add |
| **Aria2** | Edit ~/.aria2/aria2.conf → bt-tracker= |

---

### 🚀 Advanced: Docker

```bash
docker build -t trackerproxy .
docker run -p 1337:1337 trackerproxy
```

---

### 📊 Check if It's Working

```bash
# Watch tracker requests in real-time
tail -f logs/tracker_proxy.log

# Check for errors
tail -f logs/tracker_proxy_errors.log

# Search for a specific tracker
grep "tracker.opentrackr.org" logs/tracker_proxy.log
```

---

## Quick Start Italiano

### ⚡ Setup in 5 Minuti

#### 1. Installa Dipendenze Python
```bash
pip install -r requirements.txt
```

#### 2. Esegui il Server
```bash
python server.py
```

Dovresti vedere:
```
[SERVER] Loaded 120 trackers
[SERVER] Starting Flask server on 0.0.0.0:1337
```

#### 3. Configura il Tuo Client Torrent

**Esempio qBittorrent:**
1. Strumenti → Opzioni → BitTorrent
2. Trova "Tracker addizionali"
3. Aggiungi: `http://IP_TUO_SERVER:1337/announce/`
4. Clicca Applica

**Fatto!** Il tuo client torrent ora usa TrackerProxy.

---

### 🖥️ Trovare l'IP del Tuo Server

- **Stesso Computer**: `http://127.0.0.1:1337/announce/`
- **Computer in Rete**: `http://192.168.X.X:1337/announce/`
  - Trovalo: Esegui `ipconfig` (Windows) o `ifconfig` (Linux/Mac)
- **VPS/Cloud**: `http://tuo-dominio.com:1337/announce/`

---

### ⚙️ Risoluzione Problemi Base

**Problema: Il server non si avvia**
```
→ Verifica se la porta 1337 è già in uso
→ Esegui: netstat -an | grep 1337
→ Oppure cambia la porta in server.py (ultima riga)
```

**Problema: Il client torrent non trova il tracker**
```
→ Verifica il firewall (porta 1337 deve essere aperta)
→ Verifica che l'indirizzo IP sia corretto
→ Prova: curl http://127.0.0.1:1337/announce/
```

**Problema: Nessun peer viene visualizzato**
```
→ Controlla i log: tail -f logs/tracker_proxy.log
→ Cerca la riga: "SUMMARY"
→ Se tutti i tracker falliscono: aumenta UDPtimeout in settings.py
```

---

### 📋 Impostazioni

Modifica `settings.py` per personalizzare:

```python
HTTPtimeout = 2      # Secondi da aspettare per tracker HTTP
UDPtimeout = 2       # Secondi da aspettare per tracker UDP
serverListUrl = "..."  # Quale lista di tracker usare
```

#### Liste di Tracker Popolari
```python
# Migliori e più veloci (consigliato)
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"

# Più tracker, potrebbe essere più lento
"https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt"
```

---

### 📝 Configurazione Client Torrent Popolari

| Client | Passaggi |
|--------|----------|
| **qBittorrent** | Strumenti → Opzioni → BitTorrent → Tracker addizionali |
| **Transmission** | Modifica → Preferenze → Remoto → Tracker |
| **Deluge** | Preferenze → Network → Tracker → Aggiungi |
| **Aria2** | Modifica ~/.aria2/aria2.conf → bt-tracker= |

---

### 🚀 Avanzate: Docker

```bash
docker build -t trackerproxy .
docker run -p 1337:1337 trackerproxy
```

---

### 📊 Verifica che Funzioni

```bash
# Guarda le richieste ai tracker in tempo reale
tail -f logs/tracker_proxy.log

# Verifica gli errori
tail -f logs/tracker_proxy_errors.log

# Cerca un tracker specifico
grep "tracker.opentrackr.org" logs/tracker_proxy.log
```

---

For more detailed documentation, see **README.md** | Per documentazione più dettagliata, vedi **README.md**
