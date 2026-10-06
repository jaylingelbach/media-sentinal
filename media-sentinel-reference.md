# Media Sentinel — Project Reference

## 1. System Overview

Media Sentinel runs on a Raspberry Pi Zero W and monitors the Windows media PC, `Emma-PC`.

| Service | Host | Port / Method |
|---|---|---|
| Plex | `Emma-PC` | `32400` |
| Audiobookshelf | `Emma-PC` | `13378` |
| Windows Media Sentinel Agent | `Emma-PC` | `8765` |
| OLED | Media Sentinel Pi | I²C, address `0x3C` |

The monitor checks approximately every **30 seconds**.

The Windows agent reports CPU, memory, disk, and Windows uptime.

Media Sentinel uses a **3 consecutive failure** threshold before declaring a monitored service OFFLINE.

---

## 2. Development and Deployment Workflow

### Edit on the Mac

Use:

```text
Mac → VS Code → Git
```

Project directory:

```text
~/projects/media-sentinel
```

The Pi is the runtime/deployment machine. Normally, make code changes on the Mac, commit and push them with Git, then pull them onto the Pi.

### Deploy changes to the Pi

```bash
cd ~/projects/media-sentinel
git pull
sudo systemctl restart media-sentinel
sudo systemctl status media-sentinel
```

You want:

```text
Active: active (running)
```

---

## 3. Important: Don't Run `python monitor.py`

For normal operation, **do not run**:

```bash
python monitor.py
```

The application is managed by systemd.

Use:

```bash
sudo systemctl restart media-sentinel
```

instead.

This is especially important for the OLED. A manually launched `monitor.py` process can be tied to the SSH session and stop when the SSH connection ends.

The systemd service continues running after SSH disconnects.

---

## 4. Media Sentinel systemd Service

Service name:

```text
media-sentinel
```

### Restart

```bash
sudo systemctl restart media-sentinel
```

### Check status

```bash
sudo systemctl status media-sentinel
```

Look for:

```text
Active: active (running)
```

### Start

```bash
sudo systemctl start media-sentinel
```

### Stop

```bash
sudo systemctl stop media-sentinel
```

### Check whether it starts at boot

```bash
sudo systemctl is-enabled media-sentinel
```

Expected:

```text
enabled
```

### Watch live service output

```bash
sudo journalctl -u media-sentinel -f
```

This watches the running service. It does not replace the service, and the service continues running if SSH disconnects.

### Show recent service output

```bash
sudo journalctl -u media-sentinel -n 50
```

---

## 5. Media Sentinel Event Log

Application event log:

```text
logs/events.log
```

### Read entire log

```bash
cat logs/events.log
```

### Last 20 lines

```bash
tail -20 logs/events.log
```

### Follow the log live

```bash
tail -f logs/events.log
```

Press `Ctrl+C` to stop following it.

### Event log vs journal

`logs/events.log` contains application events such as:

```text
Plex OFFLINE
Plex RECOVERED
Audiobookshelf OFFLINE
Windows Agent RECOVERED
```

`journalctl` shows the output from the systemd service itself, including normal monitoring output.

---

## 6. OLED Display

Current OLED:

```text
128 × 64 SSD1306
I²C
Address: 0x3C
Bus: 1
```

### Wiring

| OLED | Raspberry Pi Zero W |
|---|---|
| GND | Physical pin 6 — GND |
| VCC | Physical pin 1 — 3.3V |
| SCL | Physical pin 5 — GPIO3 / SCL1 |
| SDA | Physical pin 3 — GPIO2 / SDA1 |

### Check the OLED

```bash
sudo i2cdetect -y 1
```

Expected address:

```text
3c
```

The OLED is on **I²C bus 1**. An empty scan on bus 2 is not the correct test.

### OLED driver

The driver is:

```text
oled.py
```

It uses the system `smbus` package directly rather than `luma.oled`.

The virtual environment was created with system site packages so the system-installed `python3-smbus` package is available:

```bash
python3 -m venv --system-site-packages .venv
```

Check:

```bash
cd ~/projects/media-sentinel
source .venv/bin/activate
python -c "import smbus; print('smbus OK')"
```

Expected:

```text
smbus OK
```

### OLED operation

`monitor.py` updates the OLED. The systemd service runs `monitor.py`, so the OLED should keep updating after SSH disconnects.

To restart it:

```bash
sudo systemctl restart media-sentinel
```

---

## 7. Windows Media PC — Emma-PC

Hostname:

```text
Emma-PC
```

### Plex

Port:

```text
32400
```

Restart Plex over SSH/PowerShell:

```powershell
Start-Process "C:\Program Files\Plex\Plex Media Server\Plex Media Server.exe"
```

### Audiobookshelf

Port:

```text
13378
```

Audiobookshelf runs in Docker on `Emma-PC`.

If ABS is unavailable, check Docker Desktop/WSL on Windows.

### Windows Media Sentinel Agent

Agent:

```text
C:\MediaSentinel\agent.ps1
```

Watchdog:

```text
C:\MediaSentinel\watchdog.ps1
```

Scheduled task:

```text
Media Sentinel Agent
```

The watchdog is used to keep the agent running.

Agent HTTP listener:

```text
http://+:8765/
```

The agent reports:

- CPU
- Memory
- Disk
- Uptime

---

## 8. Useful Windows Checks

### Check agent port

```powershell
Get-NetTCPConnection -LocalPort 8765
```

### Check HTTP URL reservation

```powershell
netsh http show urlacl
```

### Check HTTP service state

```powershell
netsh http show servicestate
```

### Check scheduled task

```powershell
Get-ScheduledTask -TaskName "Media Sentinel Agent"
```

---

## 9. Pi Shutdown

Safely shut down the Pi:

```bash
sudo shutdown -h now
```

Wait for the Pi to finish shutting down before removing power.

---

## 10. Quick "I Changed monitor.py" Procedure

### On the Mac

1. Edit in VS Code.
2. Run your local checks/syntax checks.
3. Commit the change.
4. Push with Git.

### On the Pi

```bash
cd ~/projects/media-sentinel
git pull
sudo systemctl restart media-sentinel
sudo systemctl status media-sentinel
```

Then, if you want to watch the output:

```bash
sudo journalctl -u media-sentinel -f
```

---

## 11. Troubleshooting

### OLED is blank

First check I²C:

```bash
sudo i2cdetect -y 1
```

You should see:

```text
3c
```

Then restart:

```bash
sudo systemctl restart media-sentinel
```

Check:

```bash
sudo systemctl status media-sentinel
```

Then:

```bash
sudo journalctl -u media-sentinel -f
```

### Media Sentinel is not running

```bash
sudo systemctl status media-sentinel
```

Then:

```bash
sudo journalctl -u media-sentinel -n 50
```

### Plex is OFFLINE

Check Plex on `Emma-PC`.

If necessary:

```powershell
Start-Process "C:\Program Files\Plex\Plex Media Server\Plex Media Server.exe"
```

Then give Media Sentinel a few monitoring cycles.

Remember that the current failure threshold is **3 consecutive failures**.

### Audiobookshelf is OFFLINE

Check Docker Desktop/WSL on `Emma-PC`.

ABS uses:

```text
13378
```

### Windows Agent is OFFLINE

Check:

```powershell
Get-NetTCPConnection -LocalPort 8765
```

and:

```powershell
Get-ScheduledTask -TaskName "Media Sentinel Agent"
```

---

## 12. Useful Git Commands

Check changes:

```bash
git status
```

Recent commits:

```bash
git log --oneline -10
```

Pull changes:

```bash
git pull
```

Current branch:

```bash
git branch --show-current
```

Normal deployment:

```text
Mac / VS Code
     ↓
  Git push
     ↓
    Pi
     ↓
  git pull
     ↓
systemctl restart
     ↓
Media Sentinel
```

---

## 13. Project Files

Current core project files:

```text
media-sentinel/
├── checks.py
├── monitor.py
├── oled.py
├── state.py
├── test_monitor.py
├── README.md
├── logs/
│   └── events.log
└── .venv/
```

| File | Purpose |
|---|---|
| `monitor.py` | Main monitoring loop |
| `checks.py` | Plex, Audiobookshelf, and Windows Agent checks |
| `state.py` | Failure threshold and recovery state handling |
| `oled.py` | SSD1306 OLED driver/display rendering |
| `test_monitor.py` | Monitor/state tests |
| `logs/events.log` | Persistent Media Sentinel event log |

---

## 14. Current Monitoring Behavior

Media Sentinel checks:

1. Plex
2. Audiobookshelf
3. Windows Media Sentinel Agent

Approximate interval:

```text
30 seconds
```

Failure behavior:

```text
Failure #1 → still ONLINE
Failure #2 → still ONLINE
Failure #3 → OFFLINE
```

When the service responds again, Media Sentinel logs a recovery event.

This is intentional so brief network hiccups do not immediately generate false alarms.

---

## 15. Handy Command Cheat Sheet

### Restart Media Sentinel

```bash
sudo systemctl restart media-sentinel
```

### Check Media Sentinel

```bash
sudo systemctl status media-sentinel
```

### Watch Media Sentinel

```bash
sudo journalctl -u media-sentinel -f
```

### Read event log

```bash
cat logs/events.log
```

### Last 20 event-log lines

```bash
tail -20 logs/events.log
```

### Follow event log

```bash
tail -f logs/events.log
```

### Check OLED

```bash
sudo i2cdetect -y 1
```

### Pull code changes

```bash
git pull
```

### Shut down Pi

```bash
sudo shutdown -h now
```

### Restart after pulling changes

```bash
sudo systemctl restart media-sentinel
```

---

## 16. The Most Important Things to Remember

1. **Edit code on the Mac, not the Pi.**
2. **Use Git to deploy changes to the Pi.**
3. **Do not normally run `python monitor.py` manually.**
4. **Use `sudo systemctl restart media-sentinel` to restart the application.**
5. **The OLED is controlled by the systemd service, so it continues running after SSH disconnects.**
6. **Use `sudo journalctl -u media-sentinel -f` to watch the running service.**
7. **Use `logs/events.log` for persistent application events.**
8. **The OLED is on I²C bus 1 at address `0x3C`.**
9. **Allow for the 3-failure threshold before assuming a service is actually down.**
10. **When in doubt, check `systemctl status` and `journalctl` before changing code.**
