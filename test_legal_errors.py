from datetime import date

import json

import pytest

from legal_errors import DeadlineFollowUp, MatterIntake, deadline_status, run_step


def test_deadline_decision_marks_due_follow_up():
    request = DeadlineFollowUp("MAT-7", date(2026, 9, 4), "owner")
    assert deadline_status(request, date(2026, 9, 4)) == "follow-up-due"


@pytest.mark.parametrize("matter_request, date_field", [
    (DeadlineFollowUp("MAT-7", date(2026, 9, 4), "owner"), "deadline"),
    (MatterIntake("MAT-7", "client", date(2026, 9, 4)), "received_on"),
])
def test_capture_serializes_request_dates(matter_request, date_field):
    class Capture:
        def capture(self, **payload):
            json.dumps(payload)
            assert payload["context"]["request"][date_field] == "2026-09-04"

    class Client:
        errors = Capture()

    def fail(_request):
        raise ValueError("backend failure")

    with pytest.raises(ValueError, match="backend failure"):
        run_step(Client(), "test", matter_request, fail)
