import json
import time
import urllib.error
import urllib.request


HOST = "Emma-PC"

PLEX_PORT = 32400
ABS_PORT = 13378
AGENT_PORT = 8765

FAILURE_THRESHOLD = 3

LOG_FILE = "logs/events.log"


def log_event(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as file:
        file.write(f"{timestamp} {message}\n")


def check_plex(host: str) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(
            f"http://{host}:{PLEX_PORT}/",
            timeout=3
        ) as response:

            return True, f"HTTP {response.status}"

    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            return True, f"HTTP {error.code}"

        return False, f"HTTP {error.code}"

    except urllib.error.URLError as error:
        reason = error.reason

        if isinstance(reason, TimeoutError):
            return False, "HTTP timeout"

        if isinstance(reason, ConnectionRefusedError):
            return False, "connection refused"

        return False, f"network error: {reason}"

    except TimeoutError:
        return False, "HTTP timeout"

    except OSError as error:
        return False, f"connection error: {error}"


def check_abs(host: str) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(
            f"http://{host}:{ABS_PORT}/",
            timeout=3
        ) as response:

            return True, f"HTTP {response.status}"

    except urllib.error.HTTPError as error:
        return True, f"HTTP {error.code}"

    except urllib.error.URLError as error:
        reason = error.reason

        if isinstance(reason, TimeoutError):
            return False, "HTTP timeout"

        if isinstance(reason, ConnectionRefusedError):
            return False, "connection refused"

        return False, f"network error: {reason}"

    except TimeoutError:
        return False, "HTTP timeout"

    except OSError as error:
        return False, f"connection error: {error}"


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
    failures: int,
    reason: str | None = None
) -> tuple[bool, int, str | None]:

    event = None

    if current:
        failures = 0

        if state is False:
            print(f"✅ {name} recovered")
            log_event(f"{name} RECOVERED")
            event = "RECOVERED"

        state = True

    else:
        failures += 1

        if failures >= FAILURE_THRESHOLD and state is not False:
            print(f"🚨 {name} went OFFLINE")

            if reason:
                log_event(f"{name} OFFLINE — {reason}")
            else:
                log_event(f"{name} OFFLINE")

            state = False
            event = "OFFLINE"

        elif state is None:
            state = True

    return state, failures, event


def main() -> None:
    plex_state = None
    abs_state = None
    windows_state = None

    plex_failures = 0
    abs_failures = 0
    windows_failures = 0

    while True:

        # Plex
        plex, plex_reason = check_plex(HOST)

        # Audiobookshelf
        abs_status, abs_reason = check_abs(HOST)

        # Windows health agent
        health = get_health(HOST)
        windows = health is not None

        plex_state, plex_failures, _ = update_state(
            "Plex",
            plex,
            plex_state,
            plex_failures,
            plex_reason
        )

        abs_state, abs_failures, _ = update_state(
            "Audiobookshelf",
            abs_status,
            abs_state,
            abs_failures,
            abs_reason
        )

        windows_state, windows_failures, _ = update_state(
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


if __name__ == "__main__":
    main()