# TrackerProxy

A torrent tracker proxy that aggregates requests across multiple trackers, providing a single HTTP endpoint for torrent clients.

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



### 📜 License

See LICENSE file for details.

### 🤝 Contributing

Contributions welcome! Please submit pull requests or issues.

