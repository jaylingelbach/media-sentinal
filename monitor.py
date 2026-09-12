import socket
import time


HOST = "Emma-PC"
PLEX_PORT = 32400
ABS_PORT = 13378


def check_port(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=3):
            return True
    except (TimeoutError, OSError):
        return False


while True:
    plex = check_port(HOST, PLEX_PORT)
    abs_status = check_port(HOST, ABS_PORT)

    print(f"Plex: {'ONLINE' if plex else 'OFFLINE'}")
    print(f"Audiobookshelf: {'ONLINE' if abs_status else 'OFFLINE'}")
    print()

    time.sleep(30)