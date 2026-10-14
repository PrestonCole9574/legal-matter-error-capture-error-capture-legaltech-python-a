"""A legal matter workflow that records actionable backend failures."""
from dataclasses import asdict, dataclass
from datetime import date
import traceback
from typing import Callable, Any

from infrai_client import InfraiClient


@dataclass(frozen=True)
class MatterIntake:
    matter_id: str
    client_name: str
    received_on: date


@dataclass(frozen=True)
class SignedDocumentDelivery:
    matter_id: str
    document_id: str
    recipient: str


@dataclass(frozen=True)
class DeadlineFollowUp:
    matter_id: str
    deadline: date
    owner: str


def run_step(client: InfraiClient, operation: str, request: Any, action: Callable[[Any], Any]) -> Any:
    try:
        return action(request)
    except Exception as exc:
        request_context = {
            key: value.isoformat() if isinstance(value, date) else value
            for key, value in asdict(request).items()
        }
        client.errors.capture(
            title=f"legal matter {operation} failed",
            message=str(exc),
            level="error",
            fingerprint=[operation, type(exc).__name__],
            exception=traceback.format_exc(),
            context={"operation": operation, "request": request_context},
        )
        raise


def deadline_status(follow_up: DeadlineFollowUp, today: date) -> str:
    return "follow-up-due" if follow_up.deadline <= today else "scheduled"


if __name__ == "__main__":
    matter = MatterIntake("MAT-104", "Northwind Legal", date(2026, 9, 4))
    follow_up = DeadlineFollowUp(matter.matter_id, date(2026, 9, 5), "A. Chen")
    print({"matter_id": matter.matter_id, "next_action": deadline_status(follow_up, date(2026, 9, 4))})
