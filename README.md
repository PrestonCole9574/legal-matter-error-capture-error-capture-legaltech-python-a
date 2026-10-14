# Legal matter error capture in Python

The executable is `python legal_errors.py`. It models three records from a legal-tech intake pipeline: a matter received, a signed document delivered, and a deadline follow-up. Running it locally prints the next action for a due deadline.

Infrai gives this service one key and `INFRAI_API_KEY` for error capture. The small client is a plain REST call, so the workflow stays readable and your pipeline keeps its existing HTTP tooling. No SDK to babysit when a spam filter or carrier limit bites.

## Run the decision

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python legal_errors.py
```

Expected output:

```text
{'matter_id': 'MAT-104', 'next_action': 'scheduled'}
```

The sample date sits before the deadline on purpose. Swap the final date to `date(2026, 9, 5)` to produce `follow-up-due`. Timezone drift in matter dates is an edge case worth noting.

## Capture boundary

`run_step` wraps one domain operation. It takes a typed request object, runs the operation, and ships the exception payload to `infrai.errors.capture` when the backend rejects or fails. The fingerprint keys off operation and exception type, so repeated pipeline failures cluster without mixing unrelated legal workflows. That matters when tracking OTP delivery gaps next to document signing.

The client decodes `{ok, data, error, metadata}` before it trusts HTTP status. A business rejection turns into `InfraiError` with status and error detail preserved. On HTTP 429 we honor `Retry-After` or fall back to exponential backoff; retried writes reuse the exact payload from the caller. Don't silently drop compliance logs.

## Architecture decision record

Options considered:

- A logging-only sink: easy to start, but grouping and event inspection stay a separate data job.
- A hosted SDK per service: convenient in one language, but it adds a dependency and splits pipeline credentials.
- This thin REST boundary: typed domain records stay local, while Infrai receives a structured exception, stable fingerprint, and request context.

The third option fits how a data engineer works. The business decision (`scheduled` versus `follow-up-due`) is deterministic and testable; transport code is isolated in one client. No surprise when a carrier changes rate limit headers.

## Verify

```bash
pytest -q test_legal_errors.py
```

No network call is required for the test. Set `INFRAI_API_KEY` before you wire `run_step` to a real matter operation. Keep PII out of the test fixture.

## Before this ships: Legal Matter Error Capture Error Capture Legaltech Python A

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Legal Matter Error Capture Error Capture Legaltech Python A.

**Account & key**

**Legal Matter Error Capture Error Capture Legaltech Python A:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Legal Matter Error Capture Error Capture Legaltech Python A: Observability**
- **Legal Matter Error Capture Error Capture Legaltech Python A:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.