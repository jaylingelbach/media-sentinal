from monitor import update_state


def run_test(name: str, results: list[bool]) -> None:
    print()
    print("=" * 50)
    print(name)
    print("=" * 50)

    state = None
    failures = 0

    for check_number, current in enumerate(results, start=1):

        state, failures, event = update_state(
            "TEST",
            current,
            state,
            failures,
            "simulated failure"
        )

        print(
            f"Check {check_number}: "
            f"{'ONLINE' if current else 'OFFLINE'} "
            f"→ state={state}, failures={failures}, event={event}"
        )


run_test(
    "Test 1: Three consecutive failures",
    [
        True,
        False,
        False,
        False,
    ]
)


run_test(
    "Test 2: Failure followed by recovery",
    [
        True,
        False,
        False,
        False,
        True,
    ]
)


run_test(
    "Test 3: Failure does not reach threshold",
    [
        True,
        False,
        False,
        True,
    ]
)