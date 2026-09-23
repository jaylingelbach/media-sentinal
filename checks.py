import json
import urllib.error
import urllib.request


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


def get_health(host: str) -> tuple[dict | None, str]:
    try:
        with urllib.request.urlopen(
            f"http://{host}:{AGENT_PORT}/",
            timeout=3
        ) as response:
            health = json.loads(response.read())

            return health, f"HTTP {response.status}"

    except urllib.error.HTTPError as error:
        return None, f"HTTP {error.code}"

    except urllib.error.URLError as error:
        reason = error.reason

        if isinstance(reason, TimeoutError):
            return None, "HTTP timeout"

        if isinstance(reason, ConnectionRefusedError):
            return None, "connection refused"

        return None, f"network error: {reason}"

    except TimeoutError:
        return None, "HTTP timeout"

    except json.JSONDecodeError:
        return None, "invalid JSON response"

    except OSError as error:
        return None, f"connection error: {error}"