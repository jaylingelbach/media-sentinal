from state import update_state


def test_three_failures_causes_offline():
    state = None
    failures = 0

    state, failures, event = update_state(
        True,
        state,
        failures
    )

    assert state is True
    assert failures == 0
    assert event is None

    state, failures, event = update_state(
        False,
        state,
        failures
    )

    assert state is True
    assert failures == 1
    assert event is None

    state, failures, event = update_state(
        False,
        state,
        failures
    )

    assert state is True
    assert failures == 2
    assert event is None

    state, failures, event = update_state(
        False,
        state,
        failures
    )

    assert state is False
    assert failures == 3
    assert event == "OFFLINE"


def test_recovery_after_offline():
    state = None
    failures = 0

    state, failures, event = update_state(
        True,
        state,
        failures
    )

    for _ in range(3):
        state, failures, event = update_state(
            False,
            state,
            failures
        )

    assert state is False
    assert event == "OFFLINE"

    state, failures, event = update_state(
        True,
        state,
        failures
    )

    assert state is True
    assert failures == 0
    assert event == "RECOVERED"


def test_transient_failure_does_not_cause_offline():
    state = None
    failures = 0

    state, failures, event = update_state(
        True,
        state,
        failures
    )

    state, failures, event = update_state(
        False,
        state,
        failures
    )

    state, failures, event = update_state(
        False,
        state,
        failures
    )

    assert state is True
    assert failures == 2
    assert event is None

    state, failures, event = update_state(
        True,
        state,
        failures
    )

    assert state is True
    assert failures == 0
    assert event is None


def test_offline_stays_offline():
    state = None
    failures = 0

    state, failures, event = update_state(
        True,
        state,
        failures
    )

    for _ in range(3):
        state, failures, event = update_state(
            False,
            state,
            failures
        )

    assert state is False
    assert event == "OFFLINE"

    state, failures, event = update_state(
        False,
        state,
        failures
    )

    assert state is False
    assert failures == 4
    assert event is None


print("Running Media Sentinel tests...")

test_three_failures_causes_offline()
test_recovery_after_offline()
test_transient_failure_does_not_cause_offline()
test_offline_stays_offline()

print("✅ All tests passed!")