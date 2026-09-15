import json
import socket
import time
import urllib.error
import urllib.request


HOST = "Emma-PC"

PLEX_PORT = 32400
ABS_PORT = 13378
AGENT_PORT = 8765

FAILURE_THRESHOLD = 3


def check_port(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=3):
            return True
    except (TimeoutError, OSError):
        return False


def check_plex(host: str) -> bool:
    try:
        with urllib.request.urlopen(
            f"http://{host}:{PLEX_PORT}/",
            timeout=3
        ) as response:
            return True

    except urllib.error.HTTPError as error:
        return error.code in (401, 403)

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


def update_state(
    name: str,
    current: bool,
    state: bool | None,
    failures: int
) -> tuple[bool, int]:

    if current:
        failures = 0

        if state is False:
            print(f"✅ {name} recovered")

        state = True

    else:
        failures += 1

        if failures >= FAILURE_THRESHOLD and state is not False:
            print(f"🚨 {name} went OFFLINE")
            state = False

        elif state is None:
            state = True

    return state, failures


plex_state = None
abs_state = None
windows_state = None

plex_failures = 0
abs_failures = 0
windows_failures = 0


while True:
    plex = check_plex(HOST)
    abs_status = check_port(HOST, ABS_PORT)
    health = get_health(HOST)
    windows = health is not None

    plex_state, plex_failures = update_state(
        "Plex",
        plex,
        plex_state,
        plex_failures
    )

    abs_state, abs_failures = update_state(
        "Audiobookshelf",
        abs_status,
        abs_state,
        abs_failures
    )

    windows_state, windows_failures = update_state(
        "Windows",
        windows,
        windows_state,
        windows_failures
    )

    print(f"Plex: {'ONLINE' if plex_state else 'OFFLINE'}")
    print(f"Audiobookshelf: {'ONLINE' if abs_state else 'OFFLINE'}")
    print(f"Windows health: {'ONLINE' if windows_state else 'OFFLINE'}")

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

    print()

    time.sleep(30)