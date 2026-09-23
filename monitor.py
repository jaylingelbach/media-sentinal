import time


from checks import check_plex, check_abs, get_health
from state import update_state


HOST = "Emma-PC"

LOG_FILE = "logs/events.log"


def log_event(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as file:
        file.write(f"{timestamp} {message}\n")


def handle_event(
    name: str,
    event: str | None,
    reason: str | None = None
) -> None:

    if event == "OFFLINE":
        print(f"🚨 {name} went OFFLINE")

        if reason:
            log_event(f"{name} OFFLINE — {reason}")
        else:
            log_event(f"{name} OFFLINE")

    elif event == "RECOVERED":
        print(f"✅ {name} recovered")
        log_event(f"{name} RECOVERED")


def main() -> None:
    plex_state = None
    abs_state = None
    windows_agent_state = None

    plex_failures = 0
    abs_failures = 0
    windows_agent_failures = 0

    while True:

        # Plex
        plex, plex_reason = check_plex(HOST)

        # Audiobookshelf
        abs_status, abs_reason = check_abs(HOST)

        # Windows health agent
        health, health_reason = get_health(HOST)
        windows_agent = health is not None

        # Update Plex state
        plex_state, plex_failures, plex_event = update_state(
            plex,
            plex_state,
            plex_failures
        )

        handle_event(
            "Plex",
            plex_event,
            plex_reason
        )

        # Update Audiobookshelf state
        abs_state, abs_failures, abs_event = update_state(
            abs_status,
            abs_state,
            abs_failures
        )

        handle_event(
            "Audiobookshelf",
            abs_event,
            abs_reason
        )

        # Update Windows Agent state
        windows_agent_state, windows_agent_failures, windows_agent_event = (
            update_state(
                windows_agent,
                windows_agent_state,
                windows_agent_failures
            )
        )

        handle_event(
            "Windows Agent",
            windows_agent_event,
            health_reason
        )

        print(f"Plex: {'ONLINE' if plex_state else 'OFFLINE'}")
        print(
            f"Audiobookshelf: "
            f"{'ONLINE' if abs_state else 'OFFLINE'}"
        )
        print(
            f"Windows Agent: "
            f"{'ONLINE' if windows_agent_state else 'OFFLINE'}"
        )

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