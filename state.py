# Given what I just observed, what state should this service be in?
# It doesn't know anything about Plex, ABS, Windows, logs, or networking.

FAILURE_THRESHOLD = 3


def update_state(
    current: bool,
    state: bool | None,
    failures: int
) -> tuple[bool, int, str | None]:

    event = None

    if current:
        failures = 0

        if state is False:
            event = "RECOVERED"

        state = True

    else:
        failures += 1

        if failures >= FAILURE_THRESHOLD and state is not False:
            state = False
            event = "OFFLINE"

        elif state is None:
            state = True

    return state, failures, event