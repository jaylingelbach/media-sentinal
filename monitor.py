import json
import socket
import time
import urllib.request


HOST = "Emma-PC"

PLEX_PORT = 32400
ABS_PORT = 13378
AGENT_PORT = 8765


def check_port(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=3):
            return True
    except (TimeoutError, OSError):
        return False


def get_health(host: str) -> dict | None:
    try:
        with urllib.request.urlopen(
            f"http://{host}:{AGENT_PORT}/",
            timeout=3
        ) as response:
            return json.loads(response.read())

    except (TimeoutError, OSError, json.JSONDecodeError):
        return None


def report_change(name: str, previous: bool | None, current: bool):
    if previous is None:
        return

    if previous and not current:
        print(f"🚨 {name} went OFFLINE")

    elif not previous and current:
        print(f"✅ {name} recovered")


previous_plex = None
previous_abs = None
previous_windows = None


while True:
    plex = check_port(HOST, PLEX_PORT)
    abs_status = check_port(HOST, ABS_PORT)
    health = get_health(HOST)
    windows = health is not None

    report_change("Plex", previous_plex, plex)
    report_change("Audiobookshelf", previous_abs, abs_status)
    report_change("Windows", previous_windows, windows)

    print(f"Plex: {'ONLINE' if plex else 'OFFLINE'}")
    print(f"Audiobookshelf: {'ONLINE' if abs_status else 'OFFLINE'}")

    if health:
        print(f"CPU: {health['cpu']}%")
        print(f"Memory: {health['memory']}%")
        print(f"Disk: {health['disk']}%")

        uptime = health["uptime"]
        print(
            f"Uptime: {uptime['days']}d "
            f"{uptime['hours']}h "
            f"{uptime['minutes']}m"
        )
    else:
        print("Windows health: OFFLINE")

    print()

    previous_plex = plex
    previous_abs = abs_status
    previous_windows = windows

    time.sleep(30)