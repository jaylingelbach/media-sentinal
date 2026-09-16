import json
import urllib.error
import urllib.request

# Talk to Emma-PC and find out what's happening.
# No state tracking. No logging. No infinite loop.

PLEX_PORT = 32400
ABS_PORT = 13378
AGENT_PORT = 8765


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